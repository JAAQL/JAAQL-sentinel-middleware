from jaaql.openapi.swagger_documentation import *
from jaaql.documentation.documentation_shared import gen_filtered_records, gen_arg_res_sort_pageable


TITLE = "JAAQL Sentinel"
DESCRIPTION = "The jaaql sentinel api"
FILENAME = "sentinel_api"

KEY__error_id = "id"

ARG_RES__error_id = SwaggerArgumentResponse(
    name=KEY__error_id,
    description="The id of the error",
    arg_type=str,
    example="77d23a30-56fb-4641-9b6c-6e025482c770"
)

EXAMPLE__iso_8601 = "2022-07-02T09:23:38+00:00"

KEY__created = "created"

ARG_RES__error_created = SwaggerArgumentResponse(
    name=KEY__created,
    description="ISO 8601 formatted date string with timezone",
    arg_type=str,
    example=EXAMPLE__iso_8601
)

ARG_RES__error_stacktrace = SwaggerArgumentResponse(
    name="stacktrace",
    description="The complete stacktrace of the error",
    arg_type=str,
    example=["VM147:1 Uncaught TypeError: Cannot read properties of undefined (reading 'jaaql')\n    at <anonymous>:1:16"]
)

KEY__user_agent = "user_agent"
ARG_RES__user_agent = SwaggerArgumentResponse(
    name=KEY__user_agent,
    description="The user agent (if applicable) of the browser where this error was recorded. This is encrypted when stored",
    arg_type=str,
    required=False,
    condition="If user agent is present",
    example="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
)

KEY__ip_address = "ip_address"
ARG_RES__ip_address = SwaggerArgumentResponse(
    name=KEY__ip_address,
    description="The ip address where the error originated",
    arg_type=str,
    example="93.184.216.34"
)

KEY__source_file = "source_file"
EXAMPLE__source_file = "JEQL_package.js"
KEY__source_system = "source_system"
EXAMPLE__source_system = "JAAQL-middleware-python"
KEY__file_line_number = "file_line_number"

ARG_RES__error_body = [
    SwaggerArgumentResponse(
        name=KEY__source_file,
        description="The source file which the error occurred in",
        arg_type=str,
        example=[EXAMPLE__source_file]
    ),
    SwaggerArgumentResponse(
        name="error_condensed",
        description="A condensed version of the error, used to aid grouping. If longer than 200 characters, will be truncated",
        arg_type=str,
        example=["Uncaught TypeError: Cannot read properties of undefined (reading 'jaaql')"]
    ),
    SwaggerArgumentResponse(
        name=KEY__file_line_number,
        description="The line of the file that the exception occurred at",
        arg_type=int,
        example=[123]
    ),
    SwaggerArgumentResponse(
        name="version",
        description="The version of the product that has caused the error",
        arg_type=str,
        example=["2.0.1"]
    ),
    SwaggerArgumentResponse(
        name=KEY__source_system,
        description="The system/application that originated the error",
        arg_type=str,
        example=[EXAMPLE__source_system]
    )
]

DOCUMENTATION__sentinel = SwaggerDocumentation(
    security=False,
    tags="Reporting",
    methods=SwaggerMethod(
        name="Report Error",
        description="Reports an error which is logged and potentially reported via email",
        method=REST__POST,
        body=ARG_RES__error_body + [ARG_RES__error_stacktrace, ARG_RES__user_agent]
    )
)

DOCUMENTATION__sentinel_internal_errors = SwaggerDocumentation(
    tags="Errors",
    methods=SwaggerMethod(
        name="Fetch errors",
        description="Fetches a list of errors",
        method=REST__GET,
        arguments=gen_arg_res_sort_pageable(KEY__source_file, KEY__source_system, EXAMPLE__source_file, EXAMPLE__source_system),
        response=SwaggerResponse(
            description="A list of errors",
            response=gen_filtered_records("error", ARG_RES__error_body + [ARG_RES__error_id, ARG_RES__error_created])
        )
    )
)

DOCUMENTATION__sentinel_error = SwaggerDocumentation(
    tags="Errors",
    methods=SwaggerMethod(
        name="Fetch error",
        description="Fetches detailed information on a single error",
        method=REST__GET,
        arguments=ARG_RES__error_id,
        response=SwaggerResponse(
            description="A single error",
            response=ARG_RES__error_body + [ARG_RES__error_id, ARG_RES__error_created, ARG_RES__error_stacktrace, ARG_RES__user_agent,
                                            ARG_RES__ip_address],
        )
    )
)

KEY__managed_service_name = "name"
KEY__check_every_ms = "check_every_ms"
KEY__managed_service_url = "url"
KEY__response_time_alert_threshold_ms = "response_time_alert_threshold_ms"

EXAMPLE__managed_service_name = "JAAQL"

ARG_RES__managed_service_name = SwaggerArgumentResponse(
    name=KEY__managed_service_name,
    description="The name of a managed service",
    arg_type=str,
    example=EXAMPLE__managed_service_name
)

ARG_RES__managed_service_body = [
    ARG_RES__managed_service_name,
    SwaggerArgumentResponse(
        name=KEY__check_every_ms,
        description="How many ms the service is checked at",
        arg_type=int,
        example=60 * 1000 * 5
    ),
    SwaggerArgumentResponse(
        name=KEY__managed_service_url,
        description="The url with endpoint that is called with a get request as a keep alive",
        arg_type=str,
        example="https://www.jaaql.io/api/internal/is-alive"
    ),
    SwaggerArgumentResponse(
        name=KEY__response_time_alert_threshold_ms,
        description="The threshold above which if a check takes longer than, an alert email will be triggered",
        arg_type=int,
        example=1000
    )
]

ARG_RES__check_id = SwaggerArgumentResponse(
    name="id",
    description="The id of the check",
    arg_type=str,
    example="e53487af-3c62-468c-b16d-c16017293fd5"
)

KEY__passed = "passed"
KEY__response_time_ms = "response_time_ms"
KEY__check_at = "check_at"

ARG_RES__check_body = [
    ARG_RES__check_id,
    SwaggerArgumentResponse(
        name=KEY__check_at,
        description="When the check was performed in ISO 8601 format",
        arg_type=str,
        example=EXAMPLE__iso_8601
    ),
    SwaggerArgumentResponse(
        name=KEY__response_time_ms,
        description="The amount of time taken for the service to response",
        arg_type=int,
        example=500
    ),
    SwaggerArgumentResponse(
        name=KEY__passed,
        description="Did the check pass",
        arg_type=bool
    )
]

KEY__skip_reload = "skip_reload"
KEY__most_recent_checks = "most_recent_checks"

DOCUMENTATION__sentinel_managed_service = SwaggerDocumentation(
    tags="Managed Services",
    methods=[
        SwaggerMethod(
            name="Add managed service",
            description="Adds a managed service",
            method=REST__POST,
            body=ARG_RES__managed_service_body + [SwaggerArgumentResponse(
                name=KEY__skip_reload,
                description="Whether to skip the reload of managed services",
                arg_type=bool,
                required=False,
                condition="Defaults to false"
            )]
        ),
        SwaggerMethod(
            name="Delete a managed service",
            description="Deletes a managed service",
            method=REST__DELETE,
            arguments=ARG_RES__managed_service_name
        ),
        SwaggerMethod(
            name="Fetch managed services",
            description="Fetches a list of managed services and their last 100 checks",
            method=REST__GET,
            response=SwaggerResponse(
                description="A list of managed services",
                response=SwaggerList(
                    *(ARG_RES__managed_service_body + [
                        SwaggerArgumentResponse(
                            name=KEY__most_recent_checks,
                            description="A list of the 100 most recent checks in descending order of when they occurred",
                            arg_type=SwaggerList(*ARG_RES__check_body)
                        )
                    ])
                )
            )
        )
    ]
)

DOCUMENTATION__sentinel_managed_service_paged_checks = SwaggerDocumentation(
    tags="Managed Services",
    methods=SwaggerMethod(
        name="Fetch paged service checks",
        description="Fetches a list of paged service checks",
        method=REST__GET,
        arguments=gen_arg_res_sort_pageable(KEY__managed_service_name, KEY__passed, EXAMPLE__managed_service_name, str(True)),
        response=SwaggerResponse(
            description="A list of checks",
            response=gen_filtered_records("check", ARG_RES__check_body + [ARG_RES__managed_service_name])
        )
    )
)

KEY__raw_result = "raw_result"
KEY__response_code = "response_code"

DOCUMENTATION__sentinel_managed_service_check = SwaggerDocumentation(
    tags="Managed Services",
    methods=SwaggerMethod(
        name="Fetch single service check",
        description="Fetches a single service check using it's lookup id",
        method=REST__GET,
        arguments=ARG_RES__check_id,
        response=SwaggerResponse(
            description="A single check",
            response=ARG_RES__check_body + [
                SwaggerArgumentResponse(
                    name=KEY__raw_result,
                    description="The raw result from the check",
                    arg_type=str,
                    example="OK"
                ),
                SwaggerArgumentResponse(
                    name=KEY__response_code,
                    description="The http response code returned by the managed service",
                    arg_type=int,
                    example=200
                )
            ]
        )
    )
)

DOCUMENTATION__cooldowns = SwaggerDocumentation(
    tags="Cooldowns",
    methods=SwaggerMethod(
        name="Reset cooldowns",
        description="Resets the email cooldowns. Useful for if you've deployed a fix and now want to reset the alerts",
        method=REST__POST
    )
)

DOCUMENTATION__is_alive = SwaggerDocumentation(
    security=False,
    tags="Is Alive",
    methods=SwaggerMethod(
        name="Check is alive",
        description="An endpoint that can be called by any service to see if the service is alive",
        method=REST__GET
    )
)
