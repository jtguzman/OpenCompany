#!/usr/bin/env bash
#
# OpenCompany -- manage login accounts on the EC2 host FROM your machine.
#
# Thin wrapper over `server/scripts/manage_users.py` on the host: pushes an
# ephemeral SSH key via EC2 Instance Connect (valid ~60s, so nothing long-lived
# is stored), then runs the script as `appuser` -- the owner of the 0600 .env
# that Settings reads.
#
# Every argument is forwarded verbatim:
#
#   ./deploy/ec2/users.sh list
#   ./deploy/ec2/users.sh add --email person@company.cl --name "Person Name"
#   ./deploy/ec2/users.sh passwd  --email person@company.cl
#   ./deploy/ec2/users.sh disable --email person@company.cl
#   ./deploy/ec2/users.sh remove  --email person@company.cl
#
# Requires a valid AWS session (`aws login`). Environment overrides match
# deploy.sh: OC_INSTANCE_ID, OC_HOST, OC_REGION, OC_SSH_KEY, OC_SSH_USER.
#
# Adding an account here grants access to EVERY workflow and EVERY stored API
# key -- there is no per-user isolation. See deploy/ec2/README.md.
#
set -euo pipefail

INSTANCE_ID=${OC_INSTANCE_ID:-i-075175e352f60b453}
HOST=${OC_HOST:-54.167.202.76}
REGION=${OC_REGION:-us-east-1}
SSH_KEY=${OC_SSH_KEY:-$HOME/.ssh/opencompany-ec2}
SSH_USER=${OC_SSH_USER:-ubuntu}

[[ $# -gt 0 ]] || {
    echo "usage: $0 <list|add|passwd|disable|enable|remove> [options]" >&2
    echo "       $0 add --email person@company.cl --name \"Person Name\"" >&2
    exit 2
}

AWS=$(command -v aws || echo "$HOME/.local/bin/aws")

"$AWS" sts get-caller-identity >/dev/null || {
    echo "AWS session invalid. Run: aws login" >&2; exit 1; }

"$AWS" ec2-instance-connect send-ssh-public-key \
    --instance-id "$INSTANCE_ID" \
    --instance-os-user "$SSH_USER" \
    --ssh-public-key "$(ssh-keygen -y -f "$SSH_KEY")" \
    --region "$REGION" >/dev/null

# Arguments are re-quoted with printf %q so a display name with spaces survives
# the extra shell hop; the ssh command string is parsed by the remote shell.
REMOTE_ARGS=$(printf ' %q' "$@")

ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=25 -i "$SSH_KEY" \
    "${SSH_USER}@${HOST}" \
    "cd /opt/opencompany/server && sudo -u appuser env HOME=/home/appuser \
     .venv/bin/python scripts/manage_users.py${REMOTE_ARGS}"
