import threading

from jaaql.jaaql import create_app, DEFAULT_VAULT_KEY
from mvc.controller import SentinelController
from mvc.model import SentinelModel
import sys
from jaaql.utilities.options import *
from hosted_services.patch_services import bootup
import documentation

OPT_KEY__sentinel_email_recipient = "sentinel-email-recipient"
OPT__override = [
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
    threading.Thread(target=bootup, args=[options.get(OPT_KEY__sentinel_email_recipient), DEFAULT_VAULT_KEY], daemon=True).start()

    build_app(additional_options=OPT__override)
