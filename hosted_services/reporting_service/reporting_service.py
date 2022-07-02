from jaaql.db.db_interface import DBInterface
from jaaql.utilities.utils import load_config, await_ems_startup, get_jaaql_connection, get_base_url, get_external_url, time_delta_ms
import sys
from datetime import datetime
from jaaql.constants import HEADER__security_bypass, VAULT_KEY__jaaql_local_access_key, ENDPOINT__internal_applications, KEY__application_name, \
    KEY__application_url, KEY__default_database, ENDPOINT__internal_templates, ENDPOINT__internal_accounts, KEY__recipient, KEY__template, \
    KEY__email_account_name, KEY__email_account_send_name, KEY__email_account_protocol, KEY__email_account_host, KEY__email_account_port, \
    KEY__email_account_username, KEY__password, KEY__email_template_name, KEY__account, KEY__description, KEY__app_relative_path, KEY__subject, \
    KEY__allow_signup, KEY__allow_confirm_signup_attempt, KEY__allow_reset_password, KEY__data_validation_table, KEY__data_validation_view, \
    ENDPOINT__jaaql_emails, KEY__application, KEY__parameters, CONFIG__default, KEY__configuration, KEY__role, ENDPOINT__configuration_authorizations
from flask import Flask, jsonify, request
from base64 import b64decode as b64d
from jaaql.utilities.vault import Vault, DIR__vault
from constants import *
from documentation.documentation_sentinel import KEY__error_id, KEY__source_file, KEY__file_line_number
import requests

COOLDOWN_MS__ip = 60 * 1000 * 60 * 3  # 3 hours
COOLDOWN_MS__source_file = 60 * 1000 * 60 * 6  # 6 hours
COOLDOWN_MS__line_number = 60 * 1000 * 60 * 3  # 3 hours

ATTR__error_id = "error_id"


class ReportingService:

    def __init__(self, connection: DBInterface, sentinel_email_recipient: str, external_url: str, internal_url: str, bypass_header: dict):
        self.connection = connection
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


def create_flask_app(vault_key, is_gunicorn: bool, sentinel_email_host: str, sentinel_email_port: int, sentinel_email_username: str,
                     sentinel_email_password: str, sentinel_email_recipient: str):
    config = load_config(is_gunicorn)
    await_ems_startup()
    base_url = get_base_url(config, is_gunicorn)
    vault = Vault(vault_key, DIR__vault)
    jaaql_lookup_connection = get_jaaql_connection(config, vault)

    bypass_header = {HEADER__security_bypass: vault.get_obj(VAULT_KEY__jaaql_local_access_key)}

    if not vault.has_obj(VAULT_KEY__sentinel_already_installed):
        requests.post(base_url + ENDPOINT__internal_applications, json={
            KEY__application_name: APPLICATION__sentinel,
            KEY__description: "The sentinel application",
            KEY__application_url: "{{DEFAULT}}/sentinel",
            KEY__default_database: "sentinel"
        }, headers=bypass_header)
        requests.post(base_url + ENDPOINT__configuration_authorizations, json={
            KEY__application: APPLICATION__sentinel,
            KEY__configuration: CONFIG__default,
            KEY__role: "postgres",
        }, headers=bypass_header)
        requests.post(base_url + ENDPOINT__internal_accounts, json={
            KEY__email_account_name: ACCOUNT__sentinel,
            KEY__email_account_send_name: "JAAQL Sentinel",
            KEY__email_account_protocol: "smtp",
            KEY__email_account_host: sentinel_email_host,
            KEY__email_account_port: sentinel_email_port,
            KEY__email_account_username: sentinel_email_username,
            KEY__password: b64d(sentinel_email_password).decode("ASCII")
        }, headers=bypass_header)
        requests.post(base_url + ENDPOINT__internal_templates, json={
            KEY__email_template_name: TEMPLATE__error_managed_service,
            KEY__account: ACCOUNT__sentinel,
            KEY__description: "The email that is sent when there is an error in the managed service",
            KEY__app_relative_path: "error_managed_service",
            KEY__subject: "Sentinel: Error in managed service",
            KEY__allow_signup: False,
            KEY__allow_confirm_signup_attempt: False,
            KEY__allow_reset_password: False,
            KEY__data_validation_table: "sentinel__managed_service_email",
            KEY__data_validation_view: "vw_sentinel__managed_service_error_email"
        }, headers=bypass_header)
        requests.post(base_url + ENDPOINT__internal_templates, json={
            KEY__email_template_name: TEMPLATE__error_managed_service_threshold,
            KEY__account: ACCOUNT__sentinel,
            KEY__description: "The email that is sent when a managed service keep alive exceeds it's threshold time",
            KEY__app_relative_path: "error_managed_service_threshold",
            KEY__subject: "Sentinel: Slow managed service",
            KEY__allow_signup: False,
            KEY__allow_confirm_signup_attempt: False,
            KEY__allow_reset_password: False,
            KEY__data_validation_table: "sentinel__managed_service_email",
            KEY__data_validation_view: "vw_sentinel__managed_service_threshold_email"
        }, headers=bypass_header)
        requests.post(base_url + ENDPOINT__internal_templates, json={
            KEY__email_template_name: TEMPLATE__error_reported,
            KEY__account: ACCOUNT__sentinel,
            KEY__description: "The email that is sent when an error is reported, assuming that the ip address isn't over the threshold and the line "
            "number and file have been reported once in the last 24 hours ",
            KEY__app_relative_path: "error_reported",
            KEY__subject: "Sentinel: Application error reported",
            KEY__allow_signup: False,
            KEY__allow_confirm_signup_attempt: False,
            KEY__allow_reset_password: False,
            KEY__data_validation_table: "sentinel__error_email",
            KEY__data_validation_view: "vw_sentinel__error_email"
        }, headers=bypass_header)

    vault.insert_obj(VAULT_KEY__sentinel_already_installed, "true")

    flask_app = create_app(ReportingService(jaaql_lookup_connection, sentinel_email_recipient, get_external_url(config), base_url, bypass_header))
    print("Created reporting service host, running flask", file=sys.stderr)
    flask_app.run(port=PORT__rs, host="0.0.0.0", threaded=True)
