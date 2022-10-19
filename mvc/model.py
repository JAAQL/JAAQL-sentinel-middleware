from jaaql.db.db_interface import DBInterface
from jaaql.mvc.base_model import JAAQLPivotInfo
from jaaql.mvc.model_interface import JAAQLModelInterface
from documentation.documentation_sentinel import KEY__user_agent, KEY__ip_address, KEY__most_recent_checks, KEY__skip_reload, KEY__check_at, \
    KEY__created
from jaaql.db.db_utils import execute_supplied_statement, execute_supplied_statement_singleton
from hosted_services.management_service.management import Management
from hosted_services.reporting_service.reporting import Reporting
from jaaql.exceptions.http_status_exception import HttpStatusException
from jaaql.constants import KEY__sort, SQL__desc
import traceback

ATTR__enc_ip_address = "enc_ip_address"

QUERY__ins_error = "INSERT INTO error (source_file, enc_user_agent, enc_ip_address, error_condensed, file_line_number, version, source_system, stacktrace) VALUES (:source_file, :user_agent, :ip_address, left(:error_condensed, 200), :file_line_number, :version, :source_system, :stacktrace) RETURNING enc_ip_address, id::text, source_file, file_line_number, created::text"
QUERY__sel_errors = "SELECT id, created, error_condensed, file_line_number, version, source_system, source_file FROM error"
QUERY__errors_count = "SELECT COUNT(*) FROM error"
QUERY__sel_error = "SELECT id, created, error_condensed, file_line_number, version, source_system, source_file, enc_user_agent as user_agent, enc_ip_address as ip_address, stacktrace FROM error WHERE id = :id"
QUERY__ins_managed_service = "INSERT INTO managed_service (name, check_every_ms, url, response_time_alert_threshold_ms) VALUES (:name, :check_every_ms, :url, :response_time_alert_threshold_ms)"
QUERY__del_managed_service = "DELETE FROM managed_service WHERE name = :name"
QUERY__sel_checks = "SELECT id, name, check_at, response_time_ms, passed FROM vw_managed_service_check"
QUERY__checks_count = "SELECT COUNT(*) FROM vw_managed_service_check"
QUERY__sel_check = "SELECT id, check_at, response_time_ms, passed, raw_result, response_code, passed FROM vw_managed_service_check WHERE id = :id"
QUERY__fetch_managed_services_and_recent_checks = "SELECT name, check_every_ms, url, response_time_alert_threshold_ms, id as most_recent_checks_id, check_at as most_recent_checks_check_at, response_time_ms as most_recent_checks_response_time_ms, passed as most_recent_checks_passed FROM vw_managed_service_recent_checks"

PIVOT__managed_service_check = JAAQLPivotInfo(KEY__most_recent_checks, "name", "most_recent_checks_id")


class SentinelModel(JAAQLModelInterface):

    def __init__(self):
        super().__init__()
        self.management = Management()
        self.reporting = Reporting()

    def is_alive(self):
        self.base_model.is_alive()

    def reset_cooldowns(self):
        self.management.reset_cooldowns()
        self.reporting.reset_cooldowns()

    def report_error(self, inputs: dict, ip_address: str, jaaql_connection__sentinel_live: DBInterface):
        try:
            inputs[KEY__ip_address] = ip_address
            res = execute_supplied_statement_singleton(jaaql_connection__sentinel_live, QUERY__ins_error, inputs,
                                                       encrypt_parameters=[KEY__ip_address, KEY__user_agent],
                                                       encryption_key=self.base_model.get_db_crypt_key(),
                                                       encryption_salts={KEY__ip_address: self.base_model.get_repeatable_salt()}, as_objects=True)
            self.reporting.report(res)
        except Exception as ex:
            # We cannot throw a 500 here otherwise sentinel will report itself and we will have recursion
            traceback.print_exc()
            raise HttpStatusException(str(ex))

    def fetch_errors(self, inputs: dict, connection__sentinel_live: DBInterface):
        if inputs[KEY__sort] is None or len(inputs[KEY__sort]) == 0:
            inputs[KEY__sort] = KEY__created + " " + SQL__desc

        paging_query, where_query, where_parameters, parameters = self.base_model.construct_paging_queries(inputs)
        full_query = QUERY__sel_errors + paging_query

        return self.base_model.execute_paging_query(connection__sentinel_live, full_query, QUERY__errors_count, parameters, where_query,
                                                    where_parameters)

    def fetch_error(self, inputs: dict, connection__sentinel_live: DBInterface):
        return execute_supplied_statement_singleton(connection__sentinel_live, QUERY__sel_error, inputs, as_objects=True,
                                                    encryption_key=self.base_model.get_db_crypt_key(),
                                                    decrypt_columns=[KEY__user_agent, KEY__ip_address])

    def fetch_managed_services(self, connection__sentinel_live: DBInterface):
        data = execute_supplied_statement(connection__sentinel_live, QUERY__fetch_managed_services_and_recent_checks, as_objects=True)
        return self.base_model.pivot(data, PIVOT__managed_service_check)

    def add_managed_service(self, inputs: dict, connection__sentinel_live: DBInterface):
        skip_reload = inputs.pop(KEY__skip_reload)
        execute_supplied_statement(connection__sentinel_live, QUERY__ins_managed_service, inputs)
        if not skip_reload:
            self.management.reload()

    def delete_managed_service(self, inputs: dict, connection__sentinel_live: DBInterface):
        execute_supplied_statement(connection__sentinel_live, QUERY__del_managed_service, inputs)
        self.management.reload()

    def fetch_paged_checks(self, inputs: dict, connection__sentinel_live: DBInterface):
        if inputs[KEY__sort] is None or len(inputs[KEY__sort]) == 0:
            inputs[KEY__sort] = KEY__check_at + " " + SQL__desc

        paging_query, where_query, where_parameters, parameters = self.base_model.construct_paging_queries(inputs)
        full_query = QUERY__sel_checks + paging_query

        return self.base_model.execute_paging_query(connection__sentinel_live, full_query, QUERY__checks_count, parameters, where_query,
                                                    where_parameters)

    def fetch_check(self, inputs: dict, connection__sentinel_live: DBInterface):
        return execute_supplied_statement_singleton(connection__sentinel_live, QUERY__sel_check, inputs, as_objects=True)
