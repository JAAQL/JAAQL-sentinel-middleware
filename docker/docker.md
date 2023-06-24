# Building
To build run the command directly below. It is suggested to not build however and use the command in the execution section which will pull the latest image from the docker repository

    sudo docker build -t jaaql/jaaql-sentinel-middleware -f docker/Dockerfile .

# Execution
Use the base jaaql image with these additional commands set the sentinel email account up. Create a jaaql credentials file for user @dba and a dispatcher for @dispatcher

    --mount type=bind,source="$(pwd)"/credentials-sentinel,target=/credentials \
    -e JAAQL_CONFIG_LOC=/credentials
    -e SENTINEL_APP_URL=http://my-sentinel-url \
    -e SENTINEL_EMAIL_RECIPIENT=comma_separated_recipient_emails \
    jaaql/jaaql-sentinel-middleware
