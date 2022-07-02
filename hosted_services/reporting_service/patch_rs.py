from jaaql.patch import monkey_patch

monkey_patch()

from hosted_services.reporting_service.reporting_service import create_flask_app
import os
from jaaql.constants import ENVIRON__vault_key
from constants import ENVIRON__sentinel_email_recipient

create_flask_app(os.environ.get(ENVIRON__vault_key), True, os.environ['SENTINEL_EMAIL_HOST'], int(os.environ['SENTINEL_EMAIL_PORT']),
                 os.environ['SENTINEL_EMAIL_USERNAME'], os.environ['SENTINEL_EMAIL_PASSWORD'], os.environ[ENVIRON__sentinel_email_recipient])
