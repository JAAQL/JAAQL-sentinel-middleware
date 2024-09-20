from jaaql.mvc.model_interface import JAAQLModelInterface
from documentation.documentation_sentinel import KEY__ip_address
from hosted_services.management_service.management import Management
from hosted_services.reporting_service.reporting import Reporting
from jaaql.exceptions.http_status_exception import HttpStatusException
from jaaql.constants import KEY__application
from constants import APPLICATION__sentinel, ROLE__dba
from jaaql.interpreter.interpret_jaaql import KEY_query, KEY_parameters
import traceback

QUERY__ins_error = "insert into error (location, source_file, user_agent, ip_address, error_condensed, stacktrace, file_line_number, file_col_number, version, source_system) VALUES (:location, :source_file, #user_agent, #ip_address, left(:error_condensed, 200), :stacktrace, :file_line_number, :file_col_number, :version, :source_system) RETURNING id::text as error_id, source_file, source_system, file_line_number, version, stacktrace, created::varchar"


class SentinelModel(JAAQLModelInterface):

    def __init__(self):
        super().__init__()
        self.management = Management()
        self.reporting = Reporting()

    def is_alive(self):
        self.base_model.is_alive()

    def reset_cooldowns(self, account_id):
        if account_id == ROLE__dba:
            self.management.reset_cooldowns()
            self.reporting.reset_cooldowns()
        else:
            raise HttpStatusException("Not authorised to reset cooldowns")

    def report_error(self, inputs: dict, ip_address: str):
        try:
            inputs[KEY__ip_address] = ip_address

            submit_inputs = {
                KEY_query: QUERY__ins_error,
                KEY_parameters: inputs,
                KEY__application: APPLICATION__sentinel
            }
            res = self.base_model.submit(submit_inputs, ROLE__dba, as_objects=True, singleton=True)
            res[KEY__ip_address] = ip_address

            self.reporting.report(res)
        except Exception as ex:
            # We cannot throw a 500 here otherwise sentinel will report itself and we will have recursion
            traceback.print_exc()
            raise HttpStatusException(str(ex))
