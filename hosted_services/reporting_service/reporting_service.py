from jaaql.utilities.utils import time_delta_ms
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from constants import *
from jaaql.constants import KEY__application
from documentation.documentation_sentinel import KEY__source_file, KEY__file_line_number, KEY__ip_address
from jaaql.email.email_manager import EmailManager
from jaaql.mvc.exception_queries import KG__application__artifacts_source, KG__application__base_url

COOLDOWN_MS__ip = 60 * 1000 * 60 * 3  # 3 hours
COOLDOWN_MS__source_file = 60 * 1000 * 60 * 6  # 6 hours
COOLDOWN_MS__line_number = 60 * 1000 * 60 * 3  # 3 hours

ATTR__error_id = "error_id"


class ReportingService:

    def __init__(self, vault, config, db_crypt_key, jaaql_connection, app, is_container: bool, sentinel_email_recipient: str):
        self.app = app
        self.sentinel_email_recipient = sentinel_email_recipient
        self.ip_cooldowns = {}
        self.source_file_cooldowns = {}
        self.line_number_cooldowns = {}
        self.email_manager = EmailManager(is_container)

        self.vault = vault
        self.config = config
        self.db_crypt_key = db_crypt_key
        self.jaaql_connection = jaaql_connection

    def handle_report(self, inputs: dict):
        ip_hit = inputs[KEY__ip_address]
        inputs.pop(KEY__ip_address)
        source_file_hit = inputs[KEY__application] + ":" + inputs[KEY__source_file]
        line_number_hit = source_file_hit + ":" + str(inputs[KEY__file_line_number])

        hit_ip_cooldown = ip_hit in self.ip_cooldowns and time_delta_ms(self.ip_cooldowns[ip_hit], datetime.now()) <= COOLDOWN_MS__ip
        hit_source_file_cooldown = source_file_hit in self.source_file_cooldowns and time_delta_ms(self.source_file_cooldowns[source_file_hit],
                                                                                                   datetime.now()) <= COOLDOWN_MS__source_file
        hit_line_number_cooldown = line_number_hit in self.line_number_cooldowns and time_delta_ms(self.line_number_cooldowns[line_number_hit],
                                                                                                   datetime.now()) <= COOLDOWN_MS__line_number

        if not hit_ip_cooldown and not hit_source_file_cooldown and not hit_line_number_cooldown:
            self.email_manager.send_email(self.vault, self.config, self.db_crypt_key, self.jaaql_connection, APPLICATION__sentinel,
                                          TEMPLATE__error_reported, self.app[KG__application__artifacts_source], self.app[KG__application__base_url],
                                          ROLE__dba, parameters={ATTR__error_id: inputs[ATTR__error_id]}, recipient=self.sentinel_email_recipient)

            self.ip_cooldowns[ip_hit] = datetime.now()
            self.source_file_cooldowns[source_file_hit] = datetime.now()
            self.line_number_cooldowns[line_number_hit] = datetime.now()


def create_app(ms: ReportingService):

    app = Flask(__name__, instance_relative_config=True)

    @app.route(ENDPOINT__rs_report, methods=["POST"])
    def report():
        ms.handle_report(request.json)
        return jsonify("OK")

    @app.route(ENDPOINT__reset_cooldowns, methods=["POST"])
    def reset():
        ms.ip_cooldowns = {}
        ms.source_file_cooldowns = {}
        ms.line_number_cooldowns = {}
        return jsonify("OK")

    return app


def create_flask_app(vault, config, db_crypt_key, jaaql_connection, app, is_container, sentinel_email_recipient: str):
    flask_app = create_app(ReportingService(vault, config, db_crypt_key, jaaql_connection, app, is_container, sentinel_email_recipient))
    print("Created reporting service host, running flask", file=sys.stderr)
    flask_app.run(port=PORT__rs, host="0.0.0.0", threaded=True)
