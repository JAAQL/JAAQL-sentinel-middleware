from jaaql.patch import monkey_patch

if __name__ == '__main__':
    monkey_patch()

from hosted_services.management_service.management_service import create_flask_app as m_flask_app
from hosted_services.reporting_service.reporting_service import create_flask_app as r_flask_app
from jaaql.utilities.vault import Vault, DIR__vault
import os
from jaaql.jaaql import DEFAULT_VAULT_KEY
from jaaql.mvc.generated_queries import application__select
from constants import ENVIRON__sentinel_email_recipient, APPLICATION__sentinel
from jaaql.utilities.utils import await_ems_startup, load_config, await_migrations_finished, get_jaaql_connection, get_db_crypt_key
import threading


def bootup(email_recipient: str, vault_key: str, is_gunicorn: bool = False):
    config = load_config(is_gunicorn)

    await_ems_startup()
    await_migrations_finished()

    vault = Vault(vault_key, DIR__vault)

    jaaql_connection = get_jaaql_connection(config, vault)

    app = application__select(jaaql_connection, APPLICATION__sentinel)
    db_crypt_key = get_db_crypt_key(vault)

    threading.Thread(target=m_flask_app, args=[vault, config, db_crypt_key, jaaql_connection, app, is_gunicorn, email_recipient], daemon=True).start()
    r_flask_app(vault, config, db_crypt_key, jaaql_connection, app, is_gunicorn, email_recipient)


if __name__ == "__main__":
    bootup(os.environ[ENVIRON__sentinel_email_recipient], DEFAULT_VAULT_KEY, True)
