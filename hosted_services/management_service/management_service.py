from jaaql.db.db_interface import DBInterface
from datetime import datetime
from jaaql.db.db_utils import execute_supplied_statement, execute_supplied_statement_singleton
from jaaql.utilities.utils import load_config, get_jaaql_connection, await_ems_startup, get_base_url, time_delta_ms, get_external_url
import sys
from flask import Flask, jsonify
from jaaql.utilities.vault import Vault, DIR__vault
from documentation.documentation_sentinel import KEY__skip_reload, KEY__managed_service_name, KEY__check_every_ms, KEY__managed_service_url, \
    KEY__response_time_alert_threshold_ms, KEY__raw_result, KEY__response_code, KEY__response_time_ms
from jaaql.constants import HEADER__security_bypass, VAULT_KEY__jaaql_local_access_key, ENDPOINT__is_alive, ENDPOINT__jaaql_emails, \
    KEY__application, KEY__parameters, KEY__template, KEY__recipient
import requests
from constants import ENDPOINT__ms_reload, PORT__ms, ENDPOINT__managed_services, ENDPOINT__sentinel_is_alive, APPLICATION__sentinel, \
    TEMPLATE__error_managed_service, TEMPLATE__error_managed_service_threshold, ENDPOINT__reset_cooldowns, ATTR__base_url, \
    VAULT_KEY__sentinel_already_installed
import threading
import time
import traceback

QUERY__fetch_managed_services = "SELECT * FROM sentinel__managed_service"
QUERY__ins_check = "INSERT INTO sentinel__managed_service_check (managed_service, raw_result, response_code, response_time_ms) VALUES (:managed_service, :raw_result, :response_code, :response_time_ms) RETURNING id::text as managed_service_check_id"

ATTR__managed_service = "managed_service"

ALERT__cooldown = 60 * 1000 * 60 * 3  # 3 hours
THRESHOLD_INTERNAL = 120
THRESHOLD_EXTERNAL = 150


class ManagementService:

    def __init__(self, connection: DBInterface, sentinel_email_recipient: str, external_url: str, internal_url: str, bypass_header: dict):
        self.connection = connection
        self.sentinel_email_recipient = sentinel_email_recipient
        self.managed_services = {}
        self.external_url = external_url
        self.internal_url = internal_url
        self.bypass_header = bypass_header
        self.alert_cooldowns = {}
        threading.Thread(target=self.wait_and_then_reload_managed_services, daemon=True).start()

    def wait_and_then_reload_managed_services(self):
        time.sleep(30)
        self.reload_managed_services()

    def reload_managed_services(self):
        res = execute_supplied_statement(self.connection, QUERY__fetch_managed_services, as_objects=True)
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

            inputs = {
                ATTR__managed_service: ms_name,
                KEY__response_code: status_code,
                KEY__raw_result: raw_response,
                KEY__response_time_ms: response_time_ms
            }
            email_parameters = execute_supplied_statement_singleton(self.connection, QUERY__ins_check, inputs, as_objects=True)
            email_parameters[ATTR__base_url] = self.external_url

            if self.alert_cooldowns.get(ms_name) is None or time_delta_ms(self.alert_cooldowns.get(ms_name), datetime.now()) > ALERT__cooldown:
                template = None
                if not passed:
                    template = TEMPLATE__error_managed_service
                elif response_time_ms >= ms[KEY__response_time_alert_threshold_ms]:
                    template = TEMPLATE__error_managed_service_threshold

                if template:
                    requests.post(self.internal_url + ENDPOINT__jaaql_emails, json={
                        KEY__application: APPLICATION__sentinel,
                        KEY__parameters: email_parameters,
                        KEY__template: template,
                        KEY__recipient: self.sentinel_email_recipient
                    }, headers=self.bypass_header)
                    self.alert_cooldowns[ms_name] = datetime.now()

            time.sleep(ms[KEY__check_every_ms] / 1000)

            if ms_name not in self.managed_services:
                break


def create_app(ms: ManagementService):

    app = Flask(__name__, instance_relative_config=True)

    @app.route(ENDPOINT__ms_reload, methods=["POST"])
    def reload():
        ms.reload_managed_services()
        return jsonify("OK")

    @app.route(ENDPOINT__reset_cooldowns, methods=["POST"])
    def reset():
        ms.alert_cooldowns = {}
        return jsonify("OK")

    return app


def create_flask_app(vault_key, is_gunicorn: bool, sentinel_email_recipient: str, jaaql_url: str = None):
    config = load_config(is_gunicorn)
    await_ems_startup()
    base_url = get_base_url(config, is_gunicorn)
    vault = Vault(vault_key, DIR__vault)
    jaaql_lookup_connection = get_jaaql_connection(config, vault)

    was_jaaql_url_none = jaaql_url is None

    if was_jaaql_url_none:
        jaaql_url = base_url + ENDPOINT__is_alive
    else:
        if not jaaql_url.startswith("http"):
            jaaql_url = "https://" + jaaql_url
        if not jaaql_url.endswith("/api") and not jaaql_url.endswith(ENDPOINT__is_alive):
            jaaql_url = jaaql_url + "/api"
        if not jaaql_url.endswith(ENDPOINT__is_alive):
            jaaql_url = jaaql_url + ENDPOINT__is_alive

    bypass_header = {HEADER__security_bypass: vault.get_obj(VAULT_KEY__jaaql_local_access_key)}

    if not vault.has_obj(VAULT_KEY__sentinel_already_installed):
        requests.post(base_url + ENDPOINT__managed_services, json={
            KEY__managed_service_name: "sentinel",
            KEY__check_every_ms: 60 * 1000 * 5,
            KEY__managed_service_url: base_url + ENDPOINT__sentinel_is_alive,
            KEY__response_time_alert_threshold_ms: THRESHOLD_INTERNAL,
            KEY__skip_reload: True
        }, headers=bypass_header)
        requests.post(base_url + ENDPOINT__managed_services, json={
            KEY__managed_service_name: "JAAQL",
            KEY__check_every_ms: 60 * 1000 * 5,
            KEY__managed_service_url: jaaql_url,
            KEY__response_time_alert_threshold_ms: THRESHOLD_INTERNAL if was_jaaql_url_none else THRESHOLD_EXTERNAL,
            KEY__skip_reload: True
        }, headers=bypass_header)

    flask_app = create_app(ManagementService(jaaql_lookup_connection, sentinel_email_recipient, get_external_url(config), base_url, bypass_header))
    print("Created management service host, running flask", file=sys.stderr)
    flask_app.run(port=PORT__ms, host="0.0.0.0", threaded=True)
