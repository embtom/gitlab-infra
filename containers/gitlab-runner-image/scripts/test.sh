#!/bin/bash

podman run --platform linux/amd64 \
  -it \
  --privileged \
  --rm \
  -w /usr/src \
  -v "$(pwd)":/usr/src \
  localhost/runner-test:latest \
  podman run --rm --platform linux/arm/v7 debian \
  /bin/bash -c "uname -m && dpkg --print-architecture"

podman run --platform linux/amd64 \
  -it \
  --privileged \
  --rm \
  -w /usr/src \
  -v "$(pwd)":/usr/src \
  localhost/runner-test:latest \
  podman run --rm --platform linux/arm/v7 debian \
  /bin/bash -c "uname -m && dpkg --print-architecture"
