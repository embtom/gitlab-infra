#!/usr/bin/env python3

import argparse
import json
import os
import signal
import site
import subprocess
import tempfile
from pathlib import Path

INTERRUPTED_EXIT_CODE = 128 + signal.SIGINT


def boolean(value: str) -> bool:
    match value:
        case "true":
            return True
        case "false":
            return False
        case _:
            raise argparse.ArgumentTypeError("must be true or false")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy and configure the GitLab service."
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Target host or IP address (default: localhost)",
    )
    parser.add_argument(
        "-r",
        "--recreate",
        type=boolean,
        help="Recreate volumes (true|false)",
    )
    parser.add_argument(
        "-t",
        "--tags",
        default=None,
        help=(
            "Comma-separated Ansible task tags (default: service, or "
            "provision_user when --provision-user is set without --tags)"
        ),
    )
    parser.add_argument(
        "-u",
        "--provision-user",
        metavar="NAME",
        help="Create this GitLab user if absent",
    )
    parser.add_argument(
        "-e",
        "--provision-email",
        metavar="EMAIL",
        help="Email address for --provision-user",
    )
    parser.add_argument(
        "-p",
        "--provision-password",
        metavar="PASSWORD",
        help="Password for --provision-user",
    )
    parser.add_argument(
        "-a",
        "--provision-admin",
        action="store_true",
        help="Grant admin rights to --provision-user",
    )

    args = parser.parse_args()

    if args.provision_user and (
        not args.provision_email or not args.provision_password
    ):
        parser.error(
            "--provision-user requires --provision-email and --provision-password"
        )

    if not args.provision_user and (
        args.provision_email or args.provision_password or args.provision_admin
    ):
        parser.error(
            "--provision-email, --provision-password and --provision-admin "
            "require --provision-user"
        )

    return args


def build_extra_vars(args: argparse.Namespace) -> dict[str, object]:
    extra_vars: dict[str, object] = {}

    is_local = args.host in {"localhost", "127.0.0.1", "::1"}

    if not is_local:
        extra_vars["ansible_host"] = args.host

    if args.recreate is not None:
        extra_vars["gitlab_service_volume_recreate"] = args.recreate

    if args.provision_user:
        extra_vars.update(
            {
                "gitlab_service_provision_user_name": args.provision_user,
                "gitlab_service_provision_user_email": args.provision_email,
                "gitlab_service_provision_user_password": args.provision_password,
                "gitlab_service_provision_user_admin": args.provision_admin,
            }
        )

    return extra_vars


def resolve_tags(args: argparse.Namespace) -> list[str]:
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    else:
        tags = ["provision_user"] if args.provision_user else ["service"]

    if args.provision_user and "provision_user" not in tags:
        tags.append("provision_user")

    return tags


def build_command(tags: list[str], limit: str, vars_file: Path) -> list[str]:
    return [
        "ansible-playbook",
        "--inventory",
        "inventories/hosts.yml",
        "playbooks/gitlab_setup.yml",
        "--ask-become-pass",
        "--limit",
        limit,
        "--tags",
        ",".join(tags),
        "--extra-vars",
        f"@{vars_file}",
    ]


def main() -> int:
    args = parse_args()

    is_local = args.host in {"localhost", "127.0.0.1", "::1"}
    limit = "localhost" if is_local else "remote"

    tags = resolve_tags(args)

    extra_vars = build_extra_vars(args)

    script_dir = Path(__file__).resolve().parent
    ansible_dir = script_dir.parent / "ansible"

    environment = os.environ.copy()
    user_bin = Path(site.getuserbase()) / "bin"
    environment["PATH"] = f"{environment['PATH']}:{user_bin}"

    print(f"Host: {args.host}")
    print(f"Recreate: {args.recreate}")
    print(f"Tags: {','.join(tags)}")

    with tempfile.NamedTemporaryFile(
        mode="w",
        prefix="gitlab-deploy-vars.",
        suffix=".json",
        delete=False,
    ) as vars_file:
        vars_path = Path(vars_file.name)
        os.chmod(vars_path, 0o600)
        json.dump(extra_vars, vars_file)

    try:
        command = build_command(tags, limit, vars_path)

        try:
            return subprocess.run(
                command,
                cwd=ansible_dir,
                env=environment,
                check=False,
            ).returncode
        except KeyboardInterrupt:
            return INTERRUPTED_EXIT_CODE
    finally:
        vars_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
