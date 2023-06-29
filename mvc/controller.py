from documentation.documentation_sentinel import *
from jaaql.mvc.controller_interface import JAAQLControllerInterface, BaseJAAQLController
from mvc.model import SentinelModel
from constants import *
from jaaql.constants import ENDPOINT__report_sentinel_error


class SentinelController(JAAQLControllerInterface):

    def __init__(self, model: SentinelModel):
        super().__init__()
        self.model = model

    def route(self, base_controller: BaseJAAQLController):

        @base_controller.publish_route(ENDPOINT__sentinel_is_alive, DOCUMENTATION__is_alive)
        def return_ok():
            self.model.is_alive()

        @base_controller.publish_route('/sentinel/cooldowns', DOCUMENTATION__cooldowns)
        def return_ok(account_id: str):
            self.model.reset_cooldowns(account_id)

        @base_controller.publish_route(ENDPOINT__report_sentinel_error, DOCUMENTATION__sentinel, True)
        def report_error(http_inputs: dict, ip_address: str):
            self.model.report_error(http_inputs, ip_address)
