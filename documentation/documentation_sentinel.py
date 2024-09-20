from jaaql.openapi.swagger_documentation import *


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
KEY__file_col_number = "file_col_number"

ARG_RES__error_body = [
    SwaggerArgumentResponse(
        name="location",
        description="The full url at which the error occurred",
        arg_type=str,
        example=["out-and-about"]
    ),
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
        name=KEY__file_col_number,
        description="The column of the file that the exception occurred at",
        required=False,
        condition="Sometimes not available",
        arg_type=int,
        example=[21]
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

EXAMPLE__managed_service_name = "JAAQL"

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
