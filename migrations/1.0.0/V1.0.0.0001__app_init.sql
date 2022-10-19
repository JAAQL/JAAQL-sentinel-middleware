SELECT create_tenant_application('sentinel', 'The sentinel application');
SELECT add_to_application_schema('sentinel', 'default', true);
SELECT create_application_configuration('sentinel', 'live', '{{JAAQL__BASE_URL}}/apps/sentinel/', 'apps/sentinel');
SELECT create_tenant_database('sentinel_live');
SELECT associate_database_to_application_configuration('sentinel', 'live', 'default', 'sentinel_live');

SELECT add_email_account('sentinel_email_account', 'Sentinel Admin', '{{JAAQL__SENTINEL_EMAIL_HOST}}', {{JAAQL__SENTINEL_EMAIL_PORT}}, '{{JAAQL__SENTINEL_EMAIL_USERNAME}}', '#{{JAAQL__SENTINEL_EMAIL_PASSWORD}}');
SELECT register_email_template('sentinel-error-managed-service', 'sentinel', 'Sentinel: Error in managed service', 'The sentinel error in managed service email', 'templates/error_managed_service', 'default', 'managed_service_email', 'vw_managed_service_error_email', null, true, false, false, true, false, false);
SELECT register_email_template('sentinel-error-managed-service-threshold', 'sentinel', 'Sentinel: Slow managed service', 'The sentinel slow service email', 'templates/error_managed_service_threshold', 'default', 'managed_service_email', 'vw_managed_service_threshold_email', null, false, true, false, false, true, false);
SELECT register_email_template('sentinel-error-reported', 'sentinel', 'Sentinel: Application error reported', 'The sentinel error email', 'templates/error_reported', 'default', 'error_email', 'vw_error_email', null, false, false, true, false, false, true);
SELECT associate_email_template_with_application_configuration('sentinel-error-managed-service', 'sentinel', 'live', 'sentinel_email_account');
SELECT associate_email_template_with_application_configuration('sentinel-error-managed-service-threshold', 'sentinel', 'live', 'sentinel_email_account');
SELECT associate_email_template_with_application_configuration('sentinel-error-reported', 'sentinel', 'live', 'sentinel_email_account');
