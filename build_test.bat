@echo off
ECHO This script will build jaaql sentinel and push to pypi and docker
set /p VERSION="Please input version: "
docker build -t jaaql/jaaql-sentinel-middleware -f docker/Dockerfile .
docker tag jaaql/jaaql-sentinel-middleware jaaql/jaaql-sentinel-middleware:%VERSION%
