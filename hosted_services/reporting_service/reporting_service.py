from jaaql.utilities.utils import load_config, await_ems_startup, get_base_url, get_external_url, time_delta_ms
import sys
from datetime import datetime
from jaaql.constants import HEADER__security_bypass, VAULT_KEY__jaaql_local_access_key, KEY__recipient, KEY__template, ENDPOINT__jaaql_emails, \
    KEY__application, KEY__parameters
from flask import Flask, jsonify, request
from constants import *
from documentation.documentation_sentinel import KEY__error_id, KEY__source_file, KEY__file_line_number
import requests

COOLDOWN_MS__ip = 60 * 1000 * 60 * 3  # 3 hours
COOLDOWN_MS__source_file = 60 * 1000 * 60 * 6  # 6 hours
COOLDOWN_MS__line_number = 60 * 1000 * 60 * 3  # 3 hours

ATTR__error_id = "error_id"


class ReportingService:

    def __init__(self, sentinel_email_recipient: str, external_url: str, internal_url: str, bypass_header: dict):
        self.sentinel_email_recipient = sentinel_email_recipient
        self.external_url = external_url
        self.internal_url = internal_url
        self.bypass_header = bypass_header
        self.ip_cooldowns = {}
        self.source_file_cooldowns = {}
        self.line_number_cooldowns = {}

    def handle_report(self, inputs: dict):
        ip_hit = inputs[ATTR__enc_ip_address]
        source_file_hit = inputs[KEY__source_file]
        line_number_hit = inputs[KEY__source_file] + ":" + str(inputs[KEY__file_line_number])

        hit_ip_cooldown = ip_hit in self.ip_cooldowns and time_delta_ms(self.ip_cooldowns[ip_hit], datetime.now()) <= COOLDOWN_MS__ip
        hit_source_file_cooldown = source_file_hit in self.source_file_cooldowns and time_delta_ms(self.source_file_cooldowns[source_file_hit],
                                                                                                   datetime.now()) <= COOLDOWN_MS__source_file
        hit_line_number_cooldown = line_number_hit in self.line_number_cooldowns and time_delta_ms(self.line_number_cooldowns[ip_hit],
                                                                                                   datetime.now()) <= COOLDOWN_MS__line_number

        if not hit_ip_cooldown and not hit_source_file_cooldown and not hit_line_number_cooldown:
            requests.post(self.internal_url + ENDPOINT__jaaql_emails, json={
                KEY__application: APPLICATION__sentinel,
                KEY__parameters: {ATTR__error_id: inputs[KEY__error_id], ATTR__base_url: self.external_url},
                KEY__template: TEMPLATE__error_reported,
                KEY__recipient: self.sentinel_email_recipient
            }, headers=self.bypass_header)

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


def create_flask_app(vault, is_gunicorn: bool, sentinel_email_recipient: str):
    config = load_config(is_gunicorn)
    await_ems_startup()
    base_url = get_base_url(config, is_gunicorn)

    bypass_header = {HEADER__security_bypass: vault.get_obj(VAULT_KEY__jaaql_local_access_key)}

    flask_app = create_app(ReportingService(sentinel_email_recipient, get_external_url(config), base_url, bypass_header))
    print("Created reporting service host, running flask", file=sys.stderr)
    flask_app.run(port=PORT__rs, host="0.0.0.0", threaded=True)
