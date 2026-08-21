#!/bin/sh
set -eu

ca_source=/etc/gitlab-runner/certs/root-ca.crt
ca_destination=/usr/local/share/ca-certificates/gitlab-infra-root-ca.crt

if [ -f "$ca_source" ]; then
  cp "$ca_source" "$ca_destination"
  update-ca-certificates
fi

exec "$@"
