# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-11-15

### Changed

- Updated GitLab CE to 19.5.5 and GitLab Runner to 19.5.3.
- Clarified the LDAP certificate hostname prompt with guidance for obtaining the fully qualified LDAP hostname.

## [1.0.0] - 2026-10-28

### Added

- Rootless Podman Quadlet deployment for GitLab CE, with persistent configuration, logs, and data.
- GitLab Runner support for image-pull and direct-build workflows, including registration, concurrency, and image-pull policy settings.
- User and administrator provisioning, Container Registry support, and SSH repository cloning.
- Automated PKI for the root and intermediate CAs and GitLab TLS certificate, plus operational documentation and GitHub Actions CI.

### Changed

- Extended the default GitLab TLS certificate validity to ten years.

### Security

- Enabled TLS for GitLab with a custom certificate and key.
