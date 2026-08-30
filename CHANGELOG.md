# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-08-31

### Added

- GitLab CE deployment as a rootless Podman Quadlet service.
- Configurable persistent directories for GitLab configuration, logs, and data.
- Idempotent provisioning of regular users and administrators.
- A GitLab Runner role, including registration and request-concurrency settings.
- Container registry support and SSH repository cloning.
- Public key infrastructure automation for a root CA, intermediate CA, and
  GitLab TLS certificate.
- Operational documentation for backups, restores, and common GitLab commands.
- GitHub Actions CI that installs dependencies, runs Ansible linting, and
  publishes lint results as SARIF.

### Changed

- Extended the default GitLab TLS certificate validity period to ten years.
- Added configurable job image pull policy support for GitLab Runner.

### Security

- Added TLS support for the GitLab service using a custom certificate and key.
