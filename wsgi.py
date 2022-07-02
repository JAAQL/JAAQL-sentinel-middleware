from jaaql.jaaql import create_app
from mvc.controller import SentinelController
from mvc.model import SentinelModel
import documentation as documentation
import sys
from jaaql.utilities.options import *
import threading
from hosted_services.management_service.management_service import create_flask_app as start_management_service
from hosted_services.reporting_service.reporting_service import create_flask_app as start_reporting_service
from os.path import join, dirname

OPT_KEY__sentinel_email_host = "sentinel-email-host"
OPT_KEY__sentinel_email_port = "sentinel-email-port"
OPT_KEY__sentinel_email_username = "sentinel-email-username"
OPT_KEY__sentinel_email_password = "sentinel-email-password"
OPT_KEY__sentinel_email_recipient = "sentinel-email-recipient"
OPT__override = [
    Option(
        short="sh",
        long=OPT_KEY__sentinel_email_host,
        required=True,
        description="The host for the sentinel email account",
        is_flag=False
    ),
    Option(
        short="spo",
        long=OPT_KEY__sentinel_email_port,
        required=True,
        description="The port for the sentinel email account",
        is_flag=False
    ),
    Option(
        short="su",
        long=OPT_KEY__sentinel_email_username,
        required=True,
        description="Username for sentinel email account",
        is_flag=False
    ),
    Option(
        short="spa",
        long=OPT_KEY__sentinel_email_password,
        required=True,
        description="Base 64 encoded password for sentinel email account",
        is_flag=False
    ),
    Option(
        short="sr",
        long=OPT_KEY__sentinel_email_recipient,
        required=True,
        description="The recipient(s) for sentinel emails. Comma separated",
        is_flag=False
    )
]

migration_folder = join(dirname(__file__), "migrations")
migration_project_name = "sentinel"

models = SentinelModel()
controllers = SentinelController(models)

if __name__ == '__main__':
    options = parse_options(sys.argv, False, additional_options=OPT__override)

    recipient = options.get(OPT_KEY__sentinel_email_recipient)
    threading.Thread(target=start_management_service, args=[options.get(OPT_KEY__vault_key), False, recipient], daemon=True).start()
    rs_args = [options.get(OPT_KEY__vault_key), False, options.get(OPT_KEY__sentinel_email_host), options.get(OPT_KEY__sentinel_email_port),
               options.get(OPT_KEY__sentinel_email_username), options.get(OPT_KEY__sentinel_email_password), recipient]
    threading.Thread(target=start_reporting_service, args=rs_args, daemon=True).start()

    port, flask_app = create_app(supplied_documentation=documentation, models=models,
                                 controllers=controllers,
                                 migration_folder=migration_folder,
                                 migration_project_name=migration_project_name, additional_options=OPT__override, start_email_service=True)
    flask_app.run(port=port, host="0.0.0.0", threaded=True,)
else:
    def build_app(*args, **kwargs):
        return create_app(is_gunicorn=True, supplied_documentation=documentation,
                          migration_folder=migration_folder,
                          migration_project_name=migration_project_name,
                          models=models, controllers=controllers, **kwargs)
