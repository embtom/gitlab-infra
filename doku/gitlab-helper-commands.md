# GitLab Helper Commands

This page collects small operational helpers for the running GitLab container.

## List users

Run this on the host that runs the GitLab Podman container:

```bash
podman exec -it gitlab gitlab-rails runner '
User.find_each do |user|
  puts "#{user.id}: #{user.username} | #{user.email} | admin=#{user.admin?} | confirmed=#{user.confirmed?}"
end
'
```

This prints each user with:

- user ID
- username
- email address
- admin status
- confirmed status

Use it to quickly check which users exist and whether their accounts are active.

## Set root password

Use a prompt for the password instead of hardcoding it into the shell history:

```bash
read -s GITLAB_ROOT_PASSWORD
export GITLAB_ROOT_PASSWORD

podman exec -e GITLAB_ROOT_PASSWORD \
  gitlab gitlab-rails runner '
user = User.find_by(username: "root")
raise "User root not found" unless user

user.password = ENV.fetch("GITLAB_ROOT_PASSWORD")
user.password_confirmation = ENV.fetch("GITLAB_ROOT_PASSWORD")
user.save!

puts "Password updated for #{user.username}"
'

unset GITLAB_ROOT_PASSWORD
```

This updates the root user password without exposing it in the command history.

## Show LDAP identities for a user

Use this to confirm which LDAP provider and external UID are attached to a GitLab account.

```bash
podman exec -it gitlab gitlab-rails runner '
user = User.find_by(username: "thomas")
raise "User not found" unless user

puts "Username: #{user.username}"
puts "Email: #{user.email}"
puts "LDAP identities:"

user.identities.each do |identity|
  puts "  provider=#{identity.provider} extern_uid=#{identity.extern_uid}"
end
'
```

Replace `thomas` with the username you want to inspect.

## Remove LDAP identity for a user

Use this when you need to remove the LDAP-linked identity for a specific GitLab account.

```bash
podman exec -it gitlab gitlab-rails runner '
user = User.find_by(username: "thomas")
raise "User not found" unless user

user.identities.where(provider: "ldapmain").destroy_all

puts "LDAP identity removed"
'
```

Replace `thomas` with the target username and `ldapmain` with the provider you want to remove if needed.

## Enable local password for a user

Use this when a user should be able to log in with a local GitLab password instead of relying on LDAP-only authentication.

```bash
gitlab@mars:~$ podman exec -it gitlab gitlab-rails runner '
user = User.find_by(username: "thomas")
raise "User not found" unless user

user.password = "xxxxxx"
user.password_confirmation = "xxxxxx"
user.password_automatically_set = false
user.save!

puts "Local password enabled for #{user.username}"
'
Local password enabled for thomas
gitlab@mars:~$
```

Replace `thomas` and the password value with the target account and the desired password. This explicitly disables the automatic password setting flag so the local password remains usable.

## Notes

- Replace `root` with another username if you want to change a different account.
- Run these commands only from a trusted administrative machine.
- Keep the password input private and avoid sharing it in shell logs or terminal transcripts.

## Show gitlab runner

```bash
podman exec -it gitlab gitlab-rails runner '
Ci::Runner.find_each do |runner|
  puts "#{runner.id}: #{runner.description} | status=#{runner.status} | type=#{runner.runner_type}"
end
'

```

## Delete gitlab runner

Replace `16` with the runner ID to delete. This permanently removes its GitLab
registration; stop its local service separately when applicable.

```bash
podman exec -it gitlab gitlab-rails runner '
runner = Ci::Runner.find_by(id: 16)
raise "Runner 16 not found" unless runner

runner.destroy!
puts "Deleted runner 16"
'
```
