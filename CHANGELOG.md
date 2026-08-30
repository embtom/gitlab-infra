# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-08-31

### Added

- GitLab Runner configuration supporting both image-pull and direct-build workflows
- GitLab CE deployment as a rootless Podman Quadlet service
- Configurable persistent storage for GitLab configuration, logs, and data
- Idempotent provisioning of regular users and administrators
- GitLab Runner configuration, including registration and request-concurrency settings
- Container Registry support and SSH-based repository cloning
- Automated PKI setup for a root CA, intermediate CA, and GitLab TLS certificate
- Operational documentation covering backups, restores, and common GitLab commands
- GitHub Actions CI for dependency installation, Ansible linting, and SARIF lint-result reporting

### Changed

- Extended the default GitLab TLS certificate validity period to ten years.
- Added configurable job image pull policy support for GitLab Runner.

### Security

- Added TLS support for the GitLab service using a custom certificate and key.
