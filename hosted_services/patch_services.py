from jaaql.patch import monkey_patch

if __name__ == '__main__':
    monkey_patch()

from hosted_services.management_service.management_service import create_flask_app as m_flask_app
from hosted_services.reporting_service.reporting_service import create_flask_app as r_flask_app
from jaaql.utilities.vault import Vault, DIR__vault
import os
from jaaql.constants import ENVIRON__vault_key
from constants import ENVIRON__sentinel_email_recipient
from jaaql.utilities.utils import await_ems_startup
import threading


def bootup(email_recipient: str, vault_key: str, is_gunicorn: bool = False):
    await_ems_startup()
    vault = Vault(vault_key, DIR__vault)

    threading.Thread(target=m_flask_app, args=[vault, is_gunicorn, email_recipient], daemon=True).start()
    r_flask_app(vault, is_gunicorn, email_recipient)


if __name__ == "__main__":
    bootup(os.environ[ENVIRON__sentinel_email_recipient], os.environ.get(ENVIRON__vault_key), True)
