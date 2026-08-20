#!/usr/bin/env bash
#
# OpenCompany -- server-side install / update, run ON the EC2 host as ubuntu.
#
# Mirrors the deployment strategy already in use on this box for the cobranza
# app: app tree under /opt/<app> owned by appuser, supervisor program, nginx
# vhost, certbot for TLS, artifact delivered as a tarball.
#
# Idempotent: safe to re-run for every deploy. It never rewrites an existing
# /opt/opencompany/.env (secret rotation is a data-loss event, see the
# template) and never touches the other app's vhost or supervisor program.
#
#   sudo /tmp/opencompany-deploy/deploy/ec2/bootstrap.sh \
#        --domain company.example.com --tarball /tmp/opencompany.tar.gz
#
set -euo pipefail

APP=opencompany
APP_DIR=/opt/${APP}
LOG_DIR=/var/log/${APP}
APP_USER=appuser
DOMAIN=""
TARBALL=""
SKIP_NGINX=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain)   DOMAIN="$2"; shift 2 ;;
        --tarball)  TARBALL="$2"; shift 2 ;;
        --skip-nginx) SKIP_NGINX=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

[[ -n "$TARBALL" ]] || { echo "--tarball is required" >&2; exit 2; }
[[ -f "$TARBALL" ]] || { echo "tarball not found: $TARBALL" >&2; exit 2; }
[[ $EUID -eq 0 ]] || { echo "run with sudo" >&2; exit 2; }

say() { printf '\n==> %s\n' "$*"; }

# ---------------------------------------------------------------------------
# 1. system packages
# ---------------------------------------------------------------------------
say "System packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx supervisor curl ca-certificates git openssl >/dev/null

# Node 22 -- required by the on-demand JS/TS code-execution sidecar
# (server/nodejs), which the backend spawns itself. Ubuntu 22.04 ships Node 12,
# so NodeSource is not optional.
NODE_MAJOR=$(node -v 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/' || echo 0)
if [[ "${NODE_MAJOR:-0}" -lt 22 ]]; then
    say "Installing Node.js 22 (found major: ${NODE_MAJOR:-none})"
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null
    apt-get install -y -qq nodejs >/dev/null
fi
node -v

# uv into /usr/local/bin so appuser and root resolve the same binary. The
# backend venv is built with a uv-managed CPython: server/ requires
# >=3.11,<3.13 and this release ships 3.10.
if ! command -v uv >/dev/null 2>&1; then
    say "Installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh >/dev/null
fi
uv --version

# ---------------------------------------------------------------------------
# 2. user + directories
# ---------------------------------------------------------------------------
id -u "$APP_USER" >/dev/null 2>&1 || {
    say "Creating ${APP_USER}"
    useradd --system --create-home --shell /bin/bash "$APP_USER"
}
install -d -o "$APP_USER" -g "$APP_USER" "$APP_DIR" "$APP_DIR/data"
install -d -o "$APP_USER" -g "$APP_USER" "$LOG_DIR"

# ---------------------------------------------------------------------------
# 3. stop the app before swapping the tree
# ---------------------------------------------------------------------------
if supervisorctl status "$APP" >/dev/null 2>&1; then
    say "Stopping ${APP}"
    supervisorctl stop "$APP" || true
fi

# ---------------------------------------------------------------------------
# 4. unpack the artifact
# ---------------------------------------------------------------------------
# Code only. --keep-newer-files is deliberately NOT used: the tarball is
# authoritative for code. data/ and .env are outside the tarball's paths, so
# they survive untouched.
say "Unpacking $(basename "$TARBALL")"
tar xzf "$TARBALL" -C "$APP_DIR"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

# ---------------------------------------------------------------------------
# 5. .env -- rendered once, never rewritten
# ---------------------------------------------------------------------------
# The single place port numbers live is .env.template; read it rather than
# repeating a literal here.
PORT_VALUE=$(sed -nE 's/^PYTHON_BACKEND_PORT=([0-9]+).*/\1/p' "$APP_DIR/.env.template" | head -1)
[[ -n "$PORT_VALUE" ]] || { echo "could not read PYTHON_BACKEND_PORT from .env.template" >&2; exit 1; }

if [[ -f "$APP_DIR/.env" ]]; then
    say ".env exists -- leaving it untouched"
else
    [[ -n "$DOMAIN" ]] || { echo "--domain is required on first install" >&2; exit 2; }
    say "Rendering .env"
    # .env.template FIRST, then the production overrides. Many Settings fields
    # are declared without a Python default, so a .env holding only the
    # overrides fails startup with "Field required" on a dozen Temporal keys --
    # the template is not documentation, it is the defaults file.
    #
    # Duplicate keys are safe and intentional: python-dotenv and
    # pydantic-settings both take the LAST assignment, so the appended block
    # wins over the template's dev values. Verified, not assumed.
    {
        cat "$APP_DIR/.env.template"
        printf '\n\n# ===================================================================\n'
        printf '# Production overrides (deploy/ec2/env.production.template).\n'
        printf '# Appended last on purpose: the last assignment of a key wins.\n'
        printf '# ===================================================================\n'
        sed -e "s|__OC_DOMAIN__|${DOMAIN}|g" \
            -e "s|__OC_PORT__|${PORT_VALUE}|g" \
            -e "s|__GENERATED_SECRET_KEY__|$(openssl rand -hex 32)|" \
            -e "s|__GENERATED_JWT_SECRET_KEY__|$(openssl rand -hex 32)|" \
            -e "s|__GENERATED_API_KEY_ENCRYPTION_KEY__|$(openssl rand -hex 32)|" \
            "$APP_DIR/deploy/ec2/env.production.template"
    } > "$APP_DIR/.env"
    # 0600: the file holds the credential-encryption key.
    chown "$APP_USER":"$APP_USER" "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
fi

# ---------------------------------------------------------------------------
# 6. Python venv
# ---------------------------------------------------------------------------
say "Syncing Python dependencies"
sudo -u "$APP_USER" env HOME=/home/"$APP_USER" \
    uv sync --frozen --no-dev --project "$APP_DIR/server"

# The code sidecar's bundle is prebuilt and shipped; only its runtime
# dependency (express) is installed here. Dev deps (esbuild/tsx/typescript)
# stay off the box.
if [[ -f "$APP_DIR/server/nodejs/dist/index.js" ]]; then
    say "Installing sidecar runtime deps"
    sudo -u "$APP_USER" env HOME=/home/"$APP_USER" \
        npm install --omit=dev --no-audit --no-fund --prefix "$APP_DIR/server/nodejs" >/dev/null
else
    echo "WARNING: server/nodejs/dist/index.js missing -- Code nodes will fail" >&2
fi

# ---------------------------------------------------------------------------
# 7. supervisor
# ---------------------------------------------------------------------------
say "Installing supervisor program"
sed "s|__OC_PORT__|${PORT_VALUE}|g" \
    "$APP_DIR/deploy/ec2/conf/${APP}.supervisor.conf" > "/etc/supervisor/conf.d/${APP}.conf"
supervisorctl reread
supervisorctl update

# ---------------------------------------------------------------------------
# 8. nginx
# ---------------------------------------------------------------------------
if [[ $SKIP_NGINX -eq 0 ]]; then
    if [[ -f "/etc/nginx/sites-available/${APP}" ]]; then
        # Certbot rewrites this file in place to add the 443 listener; a blind
        # overwrite would drop the TLS block and break the site.
        say "nginx vhost exists -- leaving it untouched (certbot may own it)"
    else
        [[ -n "$DOMAIN" ]] || { echo "--domain is required to write the vhost" >&2; exit 2; }
        say "Installing nginx vhost for ${DOMAIN}"
        sed -e "s|__OC_DOMAIN__|${DOMAIN}|g" -e "s|__OC_PORT__|${PORT_VALUE}|g" \
            "$APP_DIR/deploy/ec2/conf/${APP}.nginx.conf" > "/etc/nginx/sites-available/${APP}"
        ln -sfn "/etc/nginx/sites-available/${APP}" "/etc/nginx/sites-enabled/${APP}"
    fi
    nginx -t
    systemctl reload nginx
fi

# ---------------------------------------------------------------------------
# 9. start + verify
# ---------------------------------------------------------------------------
# restart, not start: `supervisorctl update` already autostarted the program,
# so `start` would answer "ERROR (already started)" and skip the reload of a
# re-deployed tree.
say "Starting ${APP}"
supervisorctl restart "$APP" || true
sleep 10
supervisorctl status "$APP" || true

say "Health check"
if curl -fsS --max-time 10 "http://127.0.0.1:${PORT_VALUE}/health" >/dev/null; then
    echo "OK: backend answering on 127.0.0.1:${PORT_VALUE}"
else
    echo "FAILED: no /health response. Last error log:" >&2
    tail -40 "${LOG_DIR}/error.log" >&2 || true
    exit 1
fi

cat <<EOF

Done.
  App tree   ${APP_DIR}
  State      ${APP_DIR}/data   (workflow.db, credentials.db, workspaces/)
  Logs       ${LOG_DIR}/app.log, ${LOG_DIR}/error.log
  Restart    sudo supervisorctl restart ${APP}

Next, once the DNS A record for the domain resolves to this host:
  sudo certbot --nginx -d <domain>
EOF
