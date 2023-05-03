# Building
To build run the command directly below. It is suggested to not build however and use the command in the execution section which will pull the latest image from the docker repository

    sudo docker build -t jaaql/jaaql-sentinel-middleware -f docker/Dockerfile .

# Execution
Use the base jaaql image with these additional commands set the sentinel email account up

    -e SENTINEL_EMAIL_RECIPIENT=comma_separated_recipient_emails \
    jaaql/jaaql-sentinel-middleware
