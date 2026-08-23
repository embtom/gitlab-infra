# GitLab Backup and Restore

This deployment runs GitLab in a rootless Podman container named `gitlab`.
GitLab backup archives created in the container at `/var/opt/gitlab/backups`
are stored on the host at `/mnt/data_gitlab/data/backups`.

Run the commands as the host user that owns and runs the GitLab Podman service
(normally `gitlab`), not as `root`.

## Create a backup

Create a GitLab application backup:

```bash
systemd-run --user --unit gitlab-backup --collect \
  podman exec gitlab gitlab-backup create
```

The command creates a timestamped `*_gitlab_backup.tar` archive in
`/mnt/data_gitlab/data/backups`. Copy that archive to independent storage.

A GitLab application backup includes GitLab data such as the database,
repositories, uploads, artifacts, LFS objects, packages, pages, and CI secure
files. It does not include the instance configuration, TLS material, or
secrets. Back up these host directories separately:

```text
/var/lib/gitlab/config
/var/lib/gitlab/logs
/mnt/data_gitlab/data
```

The configuration directory is particularly important: its `gitlab-secrets.json`
is needed to decrypt existing GitLab data after a restore.

## Restore a backup

Restore only to the same GitLab version that created the backup. For example,
a backup from `19.2.1` must be restored while the container image is also
`19.2.1`.

1. Copy the backup archive into `/mnt/data_gitlab/data/backups/` on the target
	 host. The archive must be readable by the GitLab service user.
2. Restore `/var/lib/gitlab/config`, including `gitlab-secrets.json`, from the
	 same backup set before starting the restore.
3. Confirm the application is not in use. The restore replaces the GitLab
	 database and stored data.
4. Run the restore. Use the backup identifier from the archive name, omitting
	 `_gitlab_backup.tar`:

	 ```bash
	 podman exec -it gitlab gitlab-backup restore \
		 BACKUP=1786272804_2026_08_09_19.2.1
	 ```

	 For a restore kept as a transient user service, use the command that was
	 used for the existing import:

	 ```bash
	 systemd-run --user --unit gitlab-restore --collect \
		 podman exec gitlab gitlab-backup restore \
		 BACKUP=1786272804_2026_08_09_19.2.1
	 ```

5. Restart the GitLab user service, then verify the restored instance:

	 ```bash
	 systemctl --user restart gitlab
	 podman exec gitlab gitlab-rake gitlab:check
	 ```

Replace the example identifier with the identifier of the archive being
restored. Before relying on a backup process, perform a restore test on a
separate host or isolated instance.
