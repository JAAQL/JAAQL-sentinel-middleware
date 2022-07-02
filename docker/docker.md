# Building
To build run the command directly below. It is suggested to not build however and use the command in the execution section which will pull the latest image from the docker repository

    sudo docker build -t jaaql/jaaql-sentinel-middleware -f docker/Dockerfile .

# Execution
You must set the email credentials for sentinel as well as the url that points to JAAQL so it can be polled

    sudo docker run -d \
        --mount type=bind,source="$(pwd)"/log,target=/JAAQL-sentinel-middleware/log \
        --mount type=bind,source="$(pwd)"/www,target=/JAAQL-sentinel-middleware/www \
        --mount type=bind,source="$(pwd)"/log/nginx,target=/var/log/nginx \
        --name jaaql-sentinel-middleware \
        -p 80:80 \
        -e IS_HTTPS=FALSE \
        -e POSTGRES_PASSWORD=123456 \
        -e JAAQL_VAULT_PASSWORD=pa55word \
        -e SERVER_ADDRESS=YOUR_SERVER_ADDRESS \
        -e MFA_LABEL="JAAQL Sentinel" \
        jaaql/jaaql-sentinel-middleware

If you wish to run sentinel on the same box as JAAQL, you will need to alter the published ports. You can re-mount the lets encrypt and re-use URL so that https will still be functional (but you will call it via https://jaaql.io:8443). Setting piggyback letsencrypt to true will mean that certbot will not renew the 

    -p 8080:80 \
    -p 8443:443 \
    -e PIGGYBACK_LETSENCRYPT=TRUE \

These commands set the sentinel email account up

    -e SENTINEL_EMAIL_HOST=your_email_host \
    -e SENTINEL_EMAIL_PORT=your_email_port \
    -e SENTINEL_EMAIL_USERNAME=your_login_username \
    -e SENTINEL_EMAIL_PASSWORD=base64encode(password) \
    -e SENTINEL_EMAIL_RECIPIENT=comma_separated_recipient_emails \
    -e JAAQL_URL=url_that_points_to_jaaql e.g. jaaql.io \

Helpful command for internal uses

    sudo docker run -d \
        --mount type=bind,source="$(pwd)"/log,target=/JAAQL-sentinel-middleware/log \
        --mount type=bind,source="$(pwd)"/www,target=/JAAQL-sentinel-middleware/www \
        --mount type=bind,source="$(pwd)"/log/nginx,target=/var/log/nginx \
        --mount type=bind,source="$(pwd)"../JAAQL-middleware-python/letsencrypt,target=/etc/letsencrypt \
        --name jaaql-sentinel-middleware \
        -e PIGGYBACK_LETSENCRYPT=TRUE \
        -e IS_HTTPS=TRUE \
        -e POSTGRES_PASSWORD=123456 \
        -e JAAQL_VAULT_PASSWORD=pa55word \
        -e SERVER_ADDRESS=jaaql.io \
        -e MFA_LABEL="JAAQL Sentinel" \
        -p 8443:443 \
        -e HTTPS_EMAIL=aaron.tasker@sqmi.nl \
        -e SENTINEL_EMAIL_HOST=web119.shared.hosting-login.net \
        -e SENTINEL_EMAIL_PORT=587 \
        -e SENTINEL_EMAIL_USERNAME=jaaql-component-send@sqmi.nl \
        -e SENTINEL_EMAIL_PASSWORD={{PASSWORD_BASE64_ENCODED}} \
        -e SENTINEL_EMAIL_RECIPIENT=aaron.tasker@gmail.com \
        -e JAAQL_URL=jaaql.io \
        jaaql/jaaql-sentinel-middleware
