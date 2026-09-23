#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/.."
REPOSITORY_DIR="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
RUNNER_VERSION="$(sed -n 's/^gitlab_runner_version: "\([^"]*\)"$/\1/p' \
  "${REPOSITORY_DIR}/ansible/roles/gitlab_runner/defaults/main.yml")"

if [[ -z "${RUNNER_VERSION}" ]]; then
  echo "Unable to read gitlab_runner_version from Ansible defaults." >&2
  exit 1
fi

podman build --file "${BUILD_DIR}/Containerfile" \
  --platform linux/amd64 \
  --build-arg "GITLAB_RUNNER_VERSION=${RUNNER_VERSION}" \
  --tag localhost/gitlab-runner:latest \
  "${BUILD_DIR}"
