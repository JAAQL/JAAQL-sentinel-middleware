from jaaql.exceptions.http_status_exception import HttpSingletonStatusException
from jaaql.exceptions.jaaql_interpretable_handled_errors import UnhandledQueryError
from jaaql.generated_constants import SQLState
from jaaql.patch import monkey_patch

if __name__ == '__main__':
    monkey_patch()

from hosted_services.management_service.management_service import create_flask_app as m_flask_app
from hosted_services.reporting_service.reporting_service import create_flask_app as r_flask_app
from jaaql.utilities.vault import Vault, DIR__vault
import os
import time
from jaaql.constants import ENVIRON__vault_key
from jaaql.mvc.generated_queries import application__select, KG__application__is_live
from constants import ENVIRON__sentinel_email_recipient, APPLICATION__sentinel
from jaaql.utilities.utils import await_ems_startup, load_config, await_migrations_finished, get_jaaql_connection, get_db_crypt_key
import threading


def bootup(email_recipient: str, vault_key: str, is_gunicorn: bool = False):
    config = load_config(is_gunicorn)

    await_ems_startup()
    await_migrations_finished()

    vault = Vault(vault_key, DIR__vault)

    jaaql_connection = get_jaaql_connection(config, vault)

    app = None

    print("Awaiting Sentinel app installation")
    while app is None:
        try:
            app = application__select(jaaql_connection, APPLICATION__sentinel)
        except HttpSingletonStatusException:
            pass  # Application hasn't been inserted yet
        except UnhandledQueryError as ex:
            if ex.descriptor["sqlstate"] == SQLState.UndefinedTable.value:
                pass  # Table doesn't exist. This is okay, we are just waiting for it to be created on another thread
            else:
                raise ex

        if app is not None:
            if not app[KG__application__is_live]:
                app = None

        if app is None:
            time.sleep(5)
    print("Sentinel app installed")

    db_crypt_key = get_db_crypt_key(vault)

    threading.Thread(target=m_flask_app, args=[vault, config, db_crypt_key, jaaql_connection, app, is_gunicorn, email_recipient], daemon=True).start()
    r_flask_app(vault, config, db_crypt_key, jaaql_connection, app, is_gunicorn, email_recipient)


if __name__ == "__main__":
    bootup(os.environ[ENVIRON__sentinel_email_recipient], os.environ.get(ENVIRON__vault_key), True)
