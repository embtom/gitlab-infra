# GitLab Rsync Command: Arguments Breakdown

Command:
```bash
sudo rsync -aHAXxv --numeric-ids --progress /mnt/data_gitlab/data/ /mnt/data_gitlab/data_backup/
```

Since GitLab is a complex system utilizing dedicated system users (`git`), databases, and specific Linux permissions, these flags are strictly necessary to ensure your backup remains consistent and functional.

---

### The Combined Flags (`-aHAXxv`)

* **`-a` (Archive)**: The most critical standard flag (a shortcut for `-rlptgoD`). It copies directories **recursively**, preserves **symlinks**, maintains all **timestamps**, and keeps standard **permissions** (read/write/execute) exactly as they are.
* **`-H` (Hard Links)**: GitLab (and Git itself) relies heavily on hard links. Without this flag, `rsync` would duplicate the linked data into separate files, artificially inflating your backup size and breaking the Git structure.
* **`-A` (ACLs)**: Preserves Access Control Lists. If advanced permissions are set beyond standard Linux user/group/other rules, this ensures they are backed up.
* **`-X` (Extended Attributes)**: Backs up extended file attributes (xattrs). This is vital for security modules like SELinux; missing attributes can trigger "Permission Denied" errors after a restore.
* **`-x` (One File System)**: Prevents `rsync` from crossing filesystem boundaries. If external drives or network mounts are attached *inside* the source path, they will be skipped, avoiding accidental multi-terabyte copies.
* **`-v` (Verbose)**: Makes `rsync` talkative, listing every single file on your screen as it gets copied.

---

### The Long Arguments

* **`--numeric-ids`**: Forces `rsync` to transfer exact numerical user and group IDs (e.g., UID `1001`) instead of matching them by name (e.g., `git`). This prevents permission chaos if the backup target handles user IDs differently.
* **`--progress`**: Displays a live progress bar for each file, showing the percentage complete, current transfer speed, and remaining time.
