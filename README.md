# JAAQL Sentinel
A stand alone service that deals with active monitoring of services, alerting upon slowdown or downtime and storing response of keep-alive data. Services can also contact JAAQL sentinel (UX javascript, backend services) and use the reporting. To enable this in a javascript project, see the JAAQL-sentinel project

# Local Development
Runs on python 3.8

It is recommended to use docker, please see docker/docker.md  
For local dev please execute with the following command line arguments, replacing what is within {{}} with your variables

    --vault-key 123456abcd --sentinel-email-host {{EMAIL_HOST_NAME}} --sentinel-email-port {{EMAIL_PORT}} --sentinel-email-username {{EMAIL_USERNAME}} --sentinel-email-password {{BASE64_ENCODED_EMAIL_PASSWORD}} --sentinel-email-recipient {{EMAIL_RECIPIENTS}}

# Deployment
Please read the docker/docker.md file for more instructions (it is highly recommended to deploy under docker). JAAQL sentinel middleware sits as it's own separate container that will handle failures with the JAAQL service
