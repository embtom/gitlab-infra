# GitLab Infrastructure

Ansible automation for deploying GitLab CE as a rootless Podman Quadlet service.

## Prerequisites

- Linux target with Podman and systemd user services
- Python 3 and `pipx` on the control machine
- Remote deployments require a working OpenSSH client configuration (for example, `~/.ssh/config` with the target host, user, and key), so `ssh <remote-host>` succeeds; privilege escalation is also required on remote targets

## Install Dependencies

```bash
./scripts/install-requirements
./scripts/install-ansible
```

The install scripts install the Python requirements, Ansible, `ansible-lint`, `yamllint`, and the required Ansible collections.

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

The deployment prompts for the privilege-escalation password. GitLab, including its package registry, is available at the configured external host on port `8081` by default. The container registry is enabled by default and is available at `http://<external-host>:5050`.

The role manages separate host directories for GitLab configuration, logs, and
persistent data. By default these are `/var/lib/gitlab/config`,
`/var/lib/gitlab/logs`, and `/var/lib/gitlab/data`; override
`gitlab_service_config_dir`, `gitlab_service_logs_dir`, or
`gitlab_service_data_dir` in inventory to place them on different filesystems.

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

`--provision-admin` is a flag; it takes no value. User provisioning is idempotent: an existing username or email is left unchanged.

Avoid entering production passwords directly in a shared shell history. The VS Code provisioning tasks use a masked password prompt and pass it without shell interpretation.

## Helper Commands

See [doku/gitlab-helper-commands.md](doku/gitlab-helper-commands.md) for small operational helpers, including the command to list users from the running GitLab container.

## Validation

```bash
./scripts/ansible-lint
```

## VS Code Tasks

The workspace provides tasks for installing dependencies, linting, deployment, regular-user provisioning, and administrator provisioning. Run them from **Tasks: Run Task**.
