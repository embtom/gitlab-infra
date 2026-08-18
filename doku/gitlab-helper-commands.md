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

## Notes

- Replace `root` with another username if you want to change a different account.
- Run these commands only from a trusted administrative machine.
- Keep the password input private and avoid sharing it in shell logs or terminal transcripts.


