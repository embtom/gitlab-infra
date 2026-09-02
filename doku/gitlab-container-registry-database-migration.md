# Container Registry: Migrate filesystem metadata to the database

This guide migrates metadata from an existing filesystem-based Container
Registry to the Registry database. Container images remain in the existing
Registry storage. The Registry is read-only during migration to prevent data
from changing.

> The commands assume a GitLab container named `gitlab`.
> For an Ansible-managed installation, update
> `ansible/roles/gitlab_service/templates/gitlab.rb.j2` and deploy again.
> Local changes made in the container are lost on the next deployment.

## 1. Record the initial state

Check that the Registry database exists and record the current values:

```bash
podman exec gitlab gitlab-psql -d registry -c '\dt'

podman exec gitlab gitlab-psql -d registry -c \
  'SELECT COUNT(*) AS repositories FROM repositories;'
podman exec gitlab gitlab-psql -d registry -c \
  'SELECT COUNT(*) AS manifests FROM manifests;'
podman exec gitlab gitlab-psql -d registry -c \
  'SELECT COUNT(*) AS blobs FROM blobs;'
```

## 2. Prepare the Registry for import

Temporarily add the following configuration to `gitlab.rb`. The path must
point to the existing Registry storage.

```ruby
registry['storage'] = {
  'filesystem' => {
    'rootdirectory' => '/var/opt/gitlab/gitlab-rails/shared/registry'
  },
  'maintenance' => {
    'readonly' => {
      'enabled' => true
    }
  }
}
```

Apply the configuration:

```bash
podman exec gitlab gitlab-ctl reconfigure
```

Then check the effective Registry configuration. It must contain both the
filesystem storage and an enabled database:

```bash
podman exec gitlab cat /var/opt/gitlab/registry/config.yml
```

Expected database section:

```yaml
database:
  enabled: prefer
  user: registry
  dbname: registry
  port: 5432
  sslmode: prefer
  host: /var/opt/gitlab/postgresql
```

## 3. Run the import

First, run every import phase as a dry run:

```bash
podman exec -it gitlab gitlab-ctl registry-database import \
  --dry-run --pre-import --row-count --log-to-stdout
podman exec -it gitlab gitlab-ctl registry-database import \
  --dry-run --all-repositories --row-count --log-to-stdout
podman exec -it gitlab gitlab-ctl registry-database import \
  --dry-run --common-blobs --row-count --log-to-stdout
```

If every dry run succeeds, run the same three phases without `--dry-run`:

```bash
podman exec -it gitlab gitlab-ctl registry-database import \
  --pre-import --row-count --log-to-stdout
podman exec -it gitlab gitlab-ctl registry-database import \
  --all-repositories --row-count --log-to-stdout
podman exec -it gitlab gitlab-ctl registry-database import \
  --common-blobs --row-count --log-to-stdout
```

Do not combine `--all-repositories` and `--common-blobs` in the same command.
The three phases must run in this order:

1. `--pre-import`
2. `--all-repositories`
3. `--common-blobs`

## 4. Verify the result

```bash
podman exec gitlab gitlab-psql -d registry -c \
  'SELECT COUNT(*) AS repositories FROM repositories;'
podman exec gitlab gitlab-psql -d registry -c \
  'SELECT COUNT(*) AS manifests FROM manifests;'
podman exec gitlab gitlab-psql -d registry -c \
  'SELECT COUNT(*) AS blobs FROM blobs;'

podman exec gitlab gitlab-psql -d registry -c \
  'SELECT * FROM import_statistics;'
podman exec gitlab gitlab-ctl registry-database gc-stats
```

Compare the counts with the initial state and check the import statistics for
errors.

## 5. Re-enable write access

Remove the `maintenance` section containing `readonly` from `gitlab.rb` and
apply the configuration again:

```bash
podman exec gitlab gitlab-ctl reconfigure
```

Finally, confirm that Registry storage and the database remain configured in
`/var/opt/gitlab/registry/config.yml`.
