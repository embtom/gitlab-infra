#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/.."

podman build --file "${BUILD_DIR}/Containerfile" \
  --platform linux/amd64 \
  --tag localhost/gitlab-runner:latest \
  "${BUILD_DIR}"
