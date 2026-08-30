# GitLab Infrastructure

An Ansible-based infrastructure for deploying a self-hosted GitLab CE and
GitLab Runner environment with rootless Podman and systemd Quadlet.

[![CI](https://github.com/embtom/gitlab-infra/actions/workflows/ci.yml/badge.svg)](https://github.com/embtom/gitlab-infra/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/embtom/gitlab-infra)](https://github.com/embtom/gitlab-infra/releases)

Everything needed to run an internal GitLab platform on a Linux host: source
control, package and container registries, CI execution, TLS, and operational
automation.

## Included

- GitLab CE with persistent configuration, logs, data, the package registry,
  container registry, HTTPS, and SSH repository access.
- A private root CA, intermediate CA, and GitLab TLS certificate.
- A rootless GitLab Runner with configurable concurrency, job network, pull
  policy, and custom CA trust.
- Prebuilt GHCR runner images or local builds for isolated environments.
- Idempotent deployment, user provisioning, backup guidance, CI validation,
  and versioned image releases.

## Architecture

```text
Control machine
    |
    | Ansible / SSH
    v
Linux host
    |
    +-- systemd --user
    |     |
    |     +-- gitlab user
    |     |     +-- GitLab Quadlet
    |     |           +-- GitLab container
    |     |
    |     +-- gitlab-runner user
    |           +-- GitLab Runner Quadlet
    |                 +-- GitLab Runner container
    |
    +-- Persistent GitLab / Runner storage
    |
    +-- GitLab TLS certificate and Runner CA trust
```

Ansible connects from the control machine to configure the Linux host and
create the required users, directories, certificates, and Quadlet units.
systemd starts and supervises GitLab and GitLab Runner as rootless Podman
services under the `gitlab` and `gitlab-runner` service users. The runner
registers with GitLab and launches CI jobs from the configured job image through
its rootless Podman socket. GitLab and Runner data is stored in host directories,
separate from their containers. The private root and intermediate CA keys remain
on the control machine; only the GitLab server key, certificate, and runner trust
certificate are deployed to the host.

## Prerequisites

- Linux target with Podman and systemd user services enabled
- A user account configured for rootless Podman
- systemd --user available for that user
- Python 3 and `pipx` on the control machine
- Remote deployments require a working OpenSSH client configuration (for example, `~/.ssh/config` with the target host, user, and key), so `ssh <remote-host>` succeeds; privilege escalation is also required on remote targets
- A GitLab Runner registration token when deploying a runner for the first time

## Install Dependencies

```bash
./scripts/install-requirements
./scripts/install-ansible
```

The install scripts install the Python requirements, Ansible, `ansible-lint`, `yamllint`, and the required Ansible collections.

## Configuration

Set deployment-specific values as inventory variables in
`ansible/inventories/hosts.yml`, or provide them from a separate Ansible
variable file. The role defaults are documented in
`ansible/roles/gitlab_service/defaults/main.yml`,
`ansible/roles/gitlab_runner/defaults/main.yml`, and
`ansible/roles/pki/defaults/main.yml`.

Common settings include:

```yaml
gitlab_service_external_host: gitlab.example.internal
gitlab_service_image: docker.io/gitlab/gitlab-ce:19.3.1-ce.0
gitlab_service_web_port: 8081
gitlab_service_ssh_port: 2223
gitlab_service_registry_port: 5050
gitlab_service_data_dir: /srv/gitlab/data

gitlab_runner_container_method: image-pull
gitlab_runner_image_pull_image: ghcr.io/embtom/gitlab-infra/gitlab-runner:latest
gitlab_runner_image_pull_job_image: ghcr.io/embtom/gitlab-infra/gitlab-runner-image:latest
gitlab_runner_request_concurrency: 2
```

Use release-tagged runner images in production. Set
`gitlab_runner_container_method: direct-build` to build and transfer both
runner images from the control machine instead of pulling them from GHCR.

## Deploy GitLab

Deploy locally:

```bash
./scripts/deploy.py --host localhost
```

Deploy to the remote GitLab machine:

```bash
./scripts/deploy.py --host <remote-host>
```

Recreate the GitLab data directories before deployment:

```bash
./scripts/deploy.py --host localhost --recreate true
```

Ansible uses privilege escalation for host-level configuration and directory
setup. GitLab and GitLab Runner themselves run as rootless Podman services
under their configured service users. GitLab, including its package registry,
is available at the configured external host on port `8081` by default. The
container registry is enabled by default at `https://<external-host>:5050`.

The role manages separate host directories for GitLab configuration, logs, and
persistent data. By default these are `/var/lib/gitlab/config`,
`/var/lib/gitlab/logs`, and `/var/lib/gitlab/data`; override
`gitlab_service_config_dir`, `gitlab_service_logs_dir`, or
`gitlab_service_data_dir` in inventory to place them on different filesystems.

The default service deployment also creates the local PKI required for GitLab
TLS. To generate or renew only the PKI material, run:

```bash
./scripts/deploy.py --host localhost --tags pki
```

### PKI Locations

The root CA, intermediate CA, and GitLab server certificate are generated on
the Ansible control machine, not on the managed host. By default, all source
material is stored beneath:

```text
~/.local/share/gitlab-infra/pki/
```

This directory contains the root CA in `private/`, `csr/`, and `certs/`, and
the intermediate CA plus GitLab server key and certificate beneath
`intermediate/private/`, `intermediate/csr/`, and `intermediate/certs/`.
Private CA keys remain on the control machine.

During GitLab deployment, the managed host receives these files in
`/var/lib/gitlab/config/ssl/` by default:

```text
gitlab.key  # GitLab server private key
gitlab.crt  # GitLab server certificate followed by the intermediate CA
```

When the runner role is deployed, it also receives the root CA certificate at
`/var/lib/gitlab-runner/config/certs/root-ca.crt`. Override these locations
with the corresponding `pki_*`, `gitlab_service_*`, or `gitlab_runner_*`
variables.

## Deploy GitLab Runner

Deploy the runner role separately:

```bash
./scripts/deploy.py --host localhost --tags runner
```

The first deployment requests a GitLab Runner registration token. Set runner
configuration in inventory or a variable file. By default, the role pulls the
prebuilt images published by this repository:

```yaml
gitlab_runner_container_method: image-pull
gitlab_runner_image_pull_image: ghcr.io/embtom/gitlab-infra/gitlab-runner:latest
gitlab_runner_image_pull_job_image: ghcr.io/embtom/gitlab-infra/gitlab-runner-image:latest
```

Use a release tag instead of `latest` to pin the deployed images. For an
offline build or local image customization, switch to `direct-build`; the
control machine builds both images and transfers them to the target:

```yaml
gitlab_runner_container_method: direct-build
gitlab_runner_version: "19.2.2"
```

The runner service image, job image, GitLab URL, request concurrency, and
Podman pull policy can also be overridden with the `gitlab_runner_*` variables
in `ansible/roles/gitlab_runner/defaults/main.yml`.

## Provision Users

Provision a regular user:

```bash
./scripts/deploy.py --host localhost \
  --provision-user alice \
  --provision-email alice@example.com \
  --provision-password 'choose-a-strong-password'
```

Provision an administrator:

```bash
./scripts/deploy.py --host localhost \
  --provision-user alice \
  --provision-email alice@example.com \
  --provision-password 'choose-a-strong-password' \
  --provision-admin
```

`--provision-admin` is a flag; it takes no value. User provisioning is
idempotent: existing users are not modified.

Avoid entering production passwords directly in a shared shell history. The VS Code provisioning tasks use a masked password prompt and pass it without shell interpretation.

## Helper Commands

See [doku/gitlab-helper-commands.md](doku/gitlab-helper-commands.md) for small operational helpers, including the command to list users from the running GitLab container. Backup and restore procedures are documented in [doku/gitlab-backup.md](doku/gitlab-backup.md).

## Container Images And Releases

Pull requests build both runner images as a verification step. Pushes to
`main` publish their `latest` tags to GHCR:

- `ghcr.io/embtom/gitlab-infra/gitlab-runner:latest`
- `ghcr.io/embtom/gitlab-infra/gitlab-runner-image:latest`

Run the **Release** GitHub Actions workflow manually from the default branch to
create a versioned release. It reads the newest semantic version from
`CHANGELOG.md`, promotes both `latest` images to that version, and creates the
matching GitHub release. Update the changelog before starting the workflow.

## Validation

```bash
./scripts/ansible-lint
```

## VS Code Tasks

The workspace provides tasks for installing dependencies, linting, PKI setup,
GitLab and runner deployment, and regular-user and administrator provisioning.
Run them from **Tasks: Run Task**.
