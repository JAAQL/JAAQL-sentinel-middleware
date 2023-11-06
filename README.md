# JAAQL Sentinel
A stand alone service that deals with active monitoring of services, alerting upon slowdown or downtime and storing response of keep-alive data. Services can also contact JAAQL sentinel (UX javascript, backend services) and use the reporting. To enable this in a javascript project, see the JAAQL-sentinel project

# Local Development
Runs on python 3.12

It is recommended to use docker, please see docker/docker.md  
For local dev please execute with the following command line arguments, replacing what is within {{}} with your variables

     --sentinel-email-recipient {{EMAIL_RECIPIENTS}}

And please add the environment variable

    -e JAAQL_CONFIG_LOC ...

Which will be a folder where the config lives
# Deployment
Please read the docker/docker.md file for more instructions (it is highly recommended to deploy under docker). JAAQL sentinel middleware sits as it's own separate container that will handle failures with the JAAQL service
