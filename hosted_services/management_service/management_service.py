from datetime import datetime
from jaaql.interpreter.interpret_jaaql import KEY_query
from jaaql.utilities.utils import time_delta_ms
from jaaql.db.db_utils_no_circ import submit
import sys
from flask import Flask, jsonify
from jaaql.constants import KEY__application, KEY__parameters
from jaaql.email.email_manager import EmailManager
import requests
from constants import PORT__ms, APPLICATION__sentinel, TEMPLATE__error_managed_service, \
    TEMPLATE__error_managed_service_threshold, ENDPOINT__reset_cooldowns, ROLE__dba
from jaaql.mvc.exception_queries import KG__application__artifacts_source, KG__application__base_url
import threading
import time
import traceback

KEY__response_time_ms = "response_time_ms"
KEY__response_code = "response_code"
KEY__raw_result = "raw_result"

KEY__managed_service_name = "name"
KEY__check_every_ms = "check_every_ms"
KEY__managed_service_url = "url"
KEY__response_time_alert_threshold_ms = "response_time_alert_threshold_ms"

QUERY__fetch_managed_services = "SELECT * FROM managed_service"

ATTR__managed_service = "managed_service"

ALERT__cooldown = 60 * 1000 * 60 * 3  # 3 hours
THRESHOLD_INTERNAL = 120
THRESHOLD_EXTERNAL = 150

QUERY__ins_check = "INSERT INTO managed_service_check (managed_service, raw_result, response_code, response_time_ms) VALUES (:managed_service, :raw_result, :response_code, :response_time_ms) RETURNING id::text as managed_service_check_id"


class ManagementService:

    def __init__(self, vault, config, db_crypt_key, jaaql_connection, app, is_container: bool, sentinel_email_recipient: str):
        self.app = app
        self.sentinel_email_recipient = sentinel_email_recipient
        self.managed_services = {}
        self.alert_cooldowns = {}
        self.email_manager = EmailManager(is_container)

        self.vault = vault
        self.config = config
        self.db_crypt_key = db_crypt_key
        self.jaaql_connection = jaaql_connection

        threading.Thread(target=self.wait_and_then_reload_managed_services, daemon=True).start()

    def wait_and_then_reload_managed_services(self):
        while True:
            time.sleep(30)
            self.reload_managed_services()

    def reload_managed_services(self):
        submit_inputs = {
            KEY_query: QUERY__fetch_managed_services,
            KEY__application: APPLICATION__sentinel
        }

        res = submit(self.vault, self.config, self.db_crypt_key, self.jaaql_connection, submit_inputs, ROLE__dba, as_objects=True)
        found = []

        for ms in res:
            if ms[KEY__managed_service_name] not in self.managed_services:
                self.managed_services[ms[KEY__managed_service_name]] = ms
                threading.Thread(target=self.managed_service_thread, daemon=True, args=[ms]).start()
            found.append(ms[KEY__managed_service_name])

        to_pop_keys = [name for name in self.managed_services.keys() if name not in found]
        for to_pop in to_pop_keys:
            self.managed_services.pop(to_pop)

    def managed_service_thread(self, ms: dict):
        ms_name = ms[KEY__managed_service_name]

        while True:
            passed = False
            raw_response = None
            status_code = 0

            start_time = datetime.now()
            try:
                res = requests.get(ms[KEY__managed_service_url])
                raw_response = res.text
                status_code = res.status_code
                if status_code == 200:
                    passed = True
            except Exception as ex:
                raw_response = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
            response_time_ms = time_delta_ms(start_time, datetime.now())

            submit_inputs = {
                KEY_query: QUERY__ins_check,
                KEY__application: APPLICATION__sentinel,
                KEY__parameters: {
                    ATTR__managed_service: ms_name,
                    KEY__response_code: status_code,
                    KEY__raw_result: raw_response,
                    KEY__response_time_ms: response_time_ms
                }
            }

            email_parameters = submit(self.vault, self.config, self.db_crypt_key, self.jaaql_connection, submit_inputs, ROLE__dba, as_objects=True,
                                      singleton=True)

            if self.alert_cooldowns.get(ms_name) is None or time_delta_ms(self.alert_cooldowns.get(ms_name), datetime.now()) > ALERT__cooldown:
                template = None
                if not passed:
                    template = TEMPLATE__error_managed_service
                elif response_time_ms >= ms[KEY__response_time_alert_threshold_ms]:
                    template = TEMPLATE__error_managed_service_threshold

                if template:
                    self.email_manager.send_email(self.vault, self.config, self.db_crypt_key, self.jaaql_connection, APPLICATION__sentinel,
                                                  template, self.app[KG__application__artifacts_source],
                                                  self.app[KG__application__base_url],
                                                  ROLE__dba, parameters=email_parameters, recipient=self.sentinel_email_recipient)

                    self.alert_cooldowns[ms_name] = datetime.now()

            time.sleep(ms[KEY__check_every_ms] / 1000)

            if ms_name not in self.managed_services:
                break


def create_app(ms: ManagementService):

    app = Flask(__name__, instance_relative_config=True)

    @app.route(ENDPOINT__reset_cooldowns, methods=["POST"])
    def reset():
        ms.alert_cooldowns = {}
        return jsonify("OK")

    return app


def create_flask_app(vault, config, db_crypt_key, jaaql_connection, app, is_container, sentinel_email_recipient: str):
    flask_app = create_app(ManagementService(vault, config, db_crypt_key, jaaql_connection, app, is_container, sentinel_email_recipient))
    print("Created management service host, running flask", file=sys.stderr)
    flask_app.run(port=PORT__ms, host="0.0.0.0", threaded=True)
