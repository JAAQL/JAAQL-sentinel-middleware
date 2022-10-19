from jaaql.db.db_interface import DBInterface

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

        @base_controller.cors_route(ENDPOINT__sentinel_is_alive, DOCUMENTATION__is_alive)
        def return_ok():
            self.model.is_alive()

        @base_controller.cors_route('/sentinel/cooldowns', DOCUMENTATION__cooldowns)
        def return_ok():
            return self.model.reset_cooldowns()

        @base_controller.cors_route(ENDPOINT__report_sentinel_error, DOCUMENTATION__sentinel)
        def report_error(http_inputs: dict, ip_address: str, jaaql_connection__sentinel_live: DBInterface):
            self.model.report_error(http_inputs, ip_address, jaaql_connection__sentinel_live)

        @base_controller.cors_route('/sentinel/errors', DOCUMENTATION__sentinel_internal_errors)
        def fetch_errors(http_inputs: dict, connection__sentinel_live: DBInterface):
            return self.model.fetch_errors(http_inputs, connection__sentinel_live)

        @base_controller.cors_route('/sentinel/error', DOCUMENTATION__sentinel_error)
        def fetch_error(http_inputs: dict, connection__sentinel_live: DBInterface):
            return self.model.fetch_error(http_inputs, connection__sentinel_live)

        @base_controller.cors_route(ENDPOINT__managed_services, DOCUMENTATION__sentinel_managed_service)
        def managed_services(http_inputs: dict, connection__sentinel_live: DBInterface):
            if base_controller.is_get():
                return self.model.fetch_managed_services(connection__sentinel_live)
            elif base_controller.is_post():
                return self.model.add_managed_service(http_inputs, connection__sentinel_live)
            elif base_controller.is_delete():
                return self.model.delete_managed_service(http_inputs, connection__sentinel_live)

        @base_controller.cors_route('/sentinel/managed-services/checks', DOCUMENTATION__sentinel_managed_service_paged_checks)
        def managed_services(http_inputs: dict, connection__sentinel_live: DBInterface):
            return self.model.fetch_paged_checks(http_inputs, connection__sentinel_live)

        @base_controller.cors_route('/sentinel/managed-services/check', DOCUMENTATION__sentinel_managed_service_check)
        def managed_services(http_inputs: dict, connection__sentinel_live: DBInterface):
            return self.model.fetch_check(http_inputs, connection__sentinel_live)
