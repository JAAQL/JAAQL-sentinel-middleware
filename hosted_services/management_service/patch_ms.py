from jaaql.patch import monkey_patch

monkey_patch()

from hosted_services.management_service.management_service import create_flask_app
import os
from jaaql.constants import ENVIRON__vault_key
from constants import ENVIRON__sentinel_email_recipient

jaaql_url = os.environ.get("JAAQL_URL")
if not jaaql_url:
    print("Did not receive instructions for connecting to external JAAQL. To do this please set the docker environment variable JAAQL_URL. "
          "Instructions on how to do this are in the docker/docker.md file in the repository")

create_flask_app(os.environ.get(ENVIRON__vault_key), True, os.environ[ENVIRON__sentinel_email_recipient], )
