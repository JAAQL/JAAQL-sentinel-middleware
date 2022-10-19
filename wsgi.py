import threading

from jaaql.jaaql import create_app
from mvc.controller import SentinelController
from mvc.model import SentinelModel
import sys
from jaaql.utilities.options import *
from hosted_services.patch_services import bootup
import documentation

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


models = SentinelModel()
controllers = SentinelController(models)


def build_app(*args, **kwargs):
    return create_app(models=models, controllers=controllers, supplied_documentation=documentation, **kwargs)


if __name__ == '__main__':
    options = parse_options(sys.argv, False, additional_options=OPT__override)
    threading.Thread(target=bootup, args=[options.get(OPT_KEY__sentinel_email_recipient), options.get(OPT_KEY__vault_key)], daemon=True).start()

    build_app(additional_options=OPT__override)
