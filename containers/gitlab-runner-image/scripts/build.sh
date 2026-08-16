#!/bin/bash
set -eu

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)"
BUILD_DIR="${SCRIPT_DIR}/.."

IMAGE_TAG=${1:-runner-test}

echo "Building the Podman image with tag: $IMAGE_TAG"
podman build \
  --platform linux/amd64 \
  --file "${BUILD_DIR}/Containerfile.runner" \
  --tag "$IMAGE_TAG" \
  "${BUILD_DIR}"
