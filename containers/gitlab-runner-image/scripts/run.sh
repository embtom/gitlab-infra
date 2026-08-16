#!/bin/bash
set -eu

IMAGE_TAG=${1:-runner-test:latest}

if ! systemctl --user is-active --quiet podman.socket; then
    systemctl enable --now --user podman.socket
else
    echo "Podman socket is already enabled and running."
fi

podman run -it \
	--cap-add=SYS_ADMIN \
	--network=host \
	-v "/run/user/$(id -u)/podman/podman.sock:/var/run/podman/podman.sock" \
	$IMAGE_TAG /bin/bash