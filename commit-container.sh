#!/bin/sh

docker build -t microdom-abm:latest .
docker tag microdom-abm:latest ghcr.io/wpirri/microdom-abm:latest
docker push ghcr.io/wpirri/microdom-abm:latest

