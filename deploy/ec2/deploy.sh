#!/usr/bin/env bash
#
# OpenCompany -- deploy to the shared EC2 host FROM the developer machine.
#
# Same transport the cobranza app on this host uses: EC2 Instance Connect
# pushes an ephemeral public key, then scp delivers a tarball and ssh runs the
# server-side bootstrap. No long-lived .pem is required or stored.
#
# The React client is built HERE and shipped as dist/ on purpose: `vite build`
# peaks well above what is free on a 2 GB t3.small that is already hosting
# another app, and an OOM-killed build leaves a half-written dist.
#
#   ./deploy/ec2/deploy.sh --domain company.example.com
#
# Environment overrides (defaults match the existing host):
#   OC_INSTANCE_ID, OC_HOST, OC_REGION, OC_SSH_KEY, OC_SSH_USER
#
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$REPO_ROOT"

INSTANCE_ID=${OC_INSTANCE_ID:-i-075175e352f60b453}
HOST=${OC_HOST:-54.167.202.76}
REGION=${OC_REGION:-us-east-1}
SSH_KEY=${OC_SSH_KEY:-$HOME/.ssh/id_rsa}
SSH_USER=${OC_SSH_USER:-ubuntu}
DOMAIN=""
SKIP_BUILD=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain) DOMAIN="$2"; shift 2 ;;
        --skip-build) SKIP_BUILD=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

say() { printf '\n==> %s\n' "$*"; }

AWS=$(command -v aws || echo "$HOME/.local/bin/aws")

# ---------------------------------------------------------------------------
# 1. preflight
# ---------------------------------------------------------------------------
say "Checking AWS session"
"$AWS" sts get-caller-identity >/dev/null || {
    echo "AWS session invalid. Run: aws login" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 2. build locally
# ---------------------------------------------------------------------------
if [[ $SKIP_BUILD -eq 0 ]]; then
    say "Building client + sidecar locally"
    pnpm run build
fi
[[ -f client/dist/index.html ]] || { echo "client/dist missing -- run pnpm run build" >&2; exit 1; }
[[ -f server/nodejs/dist/index.js ]] || { echo "server/nodejs/dist missing -- run pnpm run build" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 3. package
# ---------------------------------------------------------------------------
# Ships: backend source + lockfile, the prebuilt SPA, the prebuilt sidecar
# bundle, the git-tracked example workflows (core.paths reads them from
# <repo>/.opencompany/workflows, NOT from DATA_DIR), .env.template (the
# authoritative port source read by bootstrap), and deploy/ec2 itself.
# Excludes tests, caches, and every venv/node_modules -- the server rebuilds
# those.
TARBALL=/tmp/opencompany-deploy.tar.gz
say "Packaging"
tar czf "$TARBALL" \
    --exclude='.venv' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='.ruff_cache' \
    --exclude='server/tests' \
    server client/dist .opencompany/workflows .env.template deploy/ec2
du -h "$TARBALL"

# ---------------------------------------------------------------------------
# 4. push an ephemeral SSH key (valid ~60s) and upload
# ---------------------------------------------------------------------------
say "Authorizing SSH key via EC2 Instance Connect"
"$AWS" ec2-instance-connect send-ssh-public-key \
    --instance-id "$INSTANCE_ID" \
    --instance-os-user "$SSH_USER" \
    --ssh-public-key "$(ssh-keygen -y -f "$SSH_KEY")" \
    --region "$REGION" >/dev/null

SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 -i "$SSH_KEY")

say "Uploading artifact"
scp "${SSH_OPTS[@]}" "$TARBALL" "${SSH_USER}@${HOST}:/tmp/opencompany-deploy.tar.gz"

# ---------------------------------------------------------------------------
# 5. run the server-side bootstrap
# ---------------------------------------------------------------------------
# bootstrap.sh lives inside the tarball, so extract just it first, then let it
# unpack the rest into /opt/opencompany.
say "Running bootstrap on ${HOST}"
DOMAIN_ARG=""
[[ -n "$DOMAIN" ]] && DOMAIN_ARG="--domain ${DOMAIN}"
ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" bash -s <<EOF
set -euo pipefail
rm -rf /tmp/opencompany-bootstrap
mkdir -p /tmp/opencompany-bootstrap
tar xzf /tmp/opencompany-deploy.tar.gz -C /tmp/opencompany-bootstrap deploy/ec2
chmod +x /tmp/opencompany-bootstrap/deploy/ec2/bootstrap.sh
sudo /tmp/opencompany-bootstrap/deploy/ec2/bootstrap.sh ${DOMAIN_ARG} --tarball /tmp/opencompany-deploy.tar.gz
EOF

say "Deployed"
[[ -n "$DOMAIN" ]] && echo "  https://${DOMAIN}  (after: sudo certbot --nginx -d ${DOMAIN})"
echo "  Logs: ssh ${SSH_USER}@${HOST} 'sudo tail -f /var/log/opencompany/app.log'"
