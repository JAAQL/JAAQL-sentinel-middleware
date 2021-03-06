CREATE TABLE sentinel__error (
    id uuid PRIMARY KEY NOT NULL default gen_random_uuid(),
    source_file varchar(255) not null,
    enc_user_agent text,
    enc_ip_address varchar(200) not null,
    error_condensed varchar(200) not null,
    stacktrace text not null,
    file_line_number int not null,
    version varchar(20) not null,
    source_system varchar(100) not null,
    created timestamptz not null default current_timestamp
);

create index sentinel__error_ip_idx ON sentinel__error (enc_ip_address);

CREATE TABLE sentinel__error_email (
    id uuid PRIMARY KEY not null DEFAULT gen_random_uuid(),
    error_id uuid,
    base_url varchar(200) not null,
    FOREIGN KEY (error_id) REFERENCES sentinel__error ON UPDATE CASCADE ON DELETE CASCADE
);

create view vw_sentinel__error_email as (
    SELECT
        ee.id,
        ee.error_id,
        se.source_system,
        se.version,
        se.created,
        se.stacktrace,
        ee.base_url
    FROM sentinel__error_email ee
    INNER JOIN sentinel__error se on ee.error_id = se.id
);

CREATE TABLE sentinel__managed_service (
    name varchar(50) PRIMARY KEY NOT NULL,
    check_every_ms int not null,
    url varchar(255),
    response_time_alert_threshold_ms int not null
);

CREATE TABLE sentinel__managed_service_check (
    id uuid PRIMARY KEY NOT NULL default gen_random_uuid(),
    managed_service varchar(50) not null,
    FOREIGN KEY (managed_service) REFERENCES sentinel__managed_service ON UPDATE cascade ON DELETE cascade,
    check_at timestamptz not null default current_timestamp,
    raw_result text not null,
    response_code int not null,
    response_time_ms int not null
);

CREATE TABLE sentinel__managed_service_email (
    id uuid PRIMARY KEY not null DEFAULT gen_random_uuid(),
    base_url varchar(200) not null,
    managed_service_check_id uuid NOT NULL,
    FOREIGN KEY (managed_service_check_id) REFERENCES sentinel__managed_service_check ON UPDATE cascade ON DELETE cascade
);

create view vw_sentinel__managed_service_error_email as (
    SELECT
        mse.id,
        mse.managed_service_check_id,
        smsc.managed_service as name,
        smsc.check_at,
        smsc.response_code,
        smsc.raw_result,
        mse.base_url,
        ms.url
    FROM sentinel__managed_service_email mse
    INNER JOIN sentinel__managed_service_check smsc on mse.managed_service_check_id = smsc.id
    INNER JOIN sentinel__managed_service ms ON ms.name = smsc.managed_service
);

create view vw_sentinel__managed_service_threshold_email as (
    SELECT
        mse.id,
        mse.managed_service_check_id,
        mse.base_url,
        smsc.managed_service as name,
        smsc.check_at,
        smsc.response_time_ms,
        ms.response_time_alert_threshold_ms,
        ms.url
    FROM sentinel__managed_service_email mse
    INNER JOIN sentinel__managed_service_check smsc on mse.managed_service_check_id = smsc.id
    INNER JOIN sentinel__managed_service ms ON ms.name = smsc.managed_service
);

create view vw_sentinel__managed_service_check as (
    SELECT
        sms.name,
        sms.check_every_ms,
        sms.url,
        sms.response_time_alert_threshold_ms,
        msc.id,
        msc.managed_service,
        msc.check_at,
        msc.raw_result,
        msc.response_code,
        msc.response_time_ms,
        msc.response_code = 200 and msc.response_time_ms < sms.response_time_alert_threshold_ms as passed
    FROM sentinel__managed_service_check msc
    INNER JOIN sentinel__managed_service sms on msc.managed_service = sms.name
    ORDER BY check_at DESC
);

create view vw_sentinel__managed_service_recent_checks as (
    SELECT
        *
    FROM (
             SELECT
                    *,
                    ROW_NUMBER() OVER (PARTITION BY name order by check_at DESC) AS row_id
             FROM vw_sentinel__managed_service_check
         ) AS sub
    WHERE row_id < 101
    ORDER BY "name", "check_at" DESC
);
