# EC2 deployment (shared host)

Deploys OpenCompany onto the same Ubuntu 22.04 EC2 instance that already hosts
the `sl-account-receivable` (cobranza) app, using that project's strategy:

| Concern | Convention |
|---|---|
| App tree | `/opt/opencompany`, owned by `appuser` |
| Process supervision | `supervisor` program `opencompany` |
| Public entrypoint | `nginx` vhost → `127.0.0.1:<PYTHON_BACKEND_PORT>` |
| TLS | `certbot --nginx` (Let's Encrypt, auto-renew via `certbot.timer`) |
| Artifact transport | tarball over `scp`, key pushed by EC2 Instance Connect |
| Logs | `/var/log/opencompany/{app,error}.log` |

The other app is untouched: this vhost is name-based only (it does not claim the
bare IP), the supervisor program name differs, and the backend binds a different
loopback port.

## Files

- `deploy.sh` — run on your machine. Builds, packages, uploads, invokes bootstrap.
- `bootstrap.sh` — runs on the host. Installs Node 22 + uv, creates `appuser`,
  unpacks, `uv sync`, writes supervisor + nginx config, starts, health-checks.
- `conf/opencompany.supervisor.conf`, `conf/opencompany.nginx.conf` — templates
  with `__OC_PORT__` / `__OC_DOMAIN__` placeholders.
- `env.production.template` — rendered once to `/opt/opencompany/.env`.

## Deploy

```bash
aws login                                          # session must be valid
./deploy/ec2/deploy.sh --domain company.example.com
```

Re-deploys (code only, config and state preserved):

```bash
./deploy/ec2/deploy.sh                             # --domain not needed again
./deploy/ec2/deploy.sh --skip-build                # reuse the existing dist
```

## TLS

`deploy.sh` writes a port-80 vhost. Once the DNS **A record** for the domain
points at the instance's public IP:

```bash
ssh ubuntu@<host> 'sudo certbot --nginx -d company.example.com'
```

Certbot rewrites `/etc/nginx/sites-available/opencompany` in place to add the
443 listener. `bootstrap.sh` detects an existing vhost and leaves it alone from
then on, so later deploys cannot clobber the TLS block.

## Runtime shape on this host

- **Client built locally.** `vite build` peaks above the free memory on a 2 GB
  t3.small already running another app; the prebuilt `client/dist` is shipped
  and served by the backend itself (`SERVE_STATIC_CLIENT`), so there is one
  public port, not two.
- **`TEMPORAL_ENABLED=false`.** The Temporal dev server plus the worker pools
  roughly double the resident set. Workflows run on the in-process sequential
  executor instead. Flipping this on later means editing `/opt/opencompany/.env`
  and restarting — and watching memory.
- **`REDIS_ENABLED=false`** → the cache falls back to SQLite under `DATA_DIR`.
- **Auth is on** (`VITE_AUTH_ENABLED=true`, `AUTH_MODE=single`): the first
  account registered becomes the owner and registration then closes. Register
  immediately after the first deploy — until you do, the form is open to anyone
  who finds the host. Further logins come from the operator CLI, see
  [Adding users](#adding-users).
- **Python.** `server/` requires 3.11–3.12 and this Ubuntu release ships 3.10,
  so `uv sync` provisions a uv-managed CPython. Nothing depends on the system
  interpreter.

## Adding users

Registration is closed once the owner account exists, and there is no admin UI.
Add further logins with the operator CLI on the host — as `appuser`, because
`/opt/opencompany/.env` is `0600` and owned by it:

```bash
cd /opt/opencompany/server
sudo -u appuser env HOME=/home/appuser .venv/bin/python scripts/manage_users.py list
sudo -u appuser env HOME=/home/appuser .venv/bin/python scripts/manage_users.py \
    add --email person@example.com --name "Person Name"
```

`add` prints a generated password once (only the bcrypt hash is stored); pass
`--password` to set your own. The other subcommands are `passwd`, `disable` /
`enable` (reversible, keeps the row) and `remove` (drops it). No restart needed.

The address must be one the login form accepts — `LoginRequest.email` is an
`EmailStr`, so reserved domains like `example.invalid` or a bare `localhost` are
refused at creation time rather than producing an account that cannot sign in.

**This adds a login, not a tenant.** Every account shares one workflow store and
one credential store, so a new user can see and edit every workflow and use
every API key stored in the Credentials panel. Only add people who should have
that. `AUTH_MODE=multi` (open self-registration) has exactly the same sharing
plus no gate on who signs up — see
[authentication.md](../../docs-internal/authentication.md) Known Limitations.

## State and backups

Everything stateful is under `/opt/opencompany/data`:

```
workflow.db        workflows, settings, executions
credentials.db     Fernet-encrypted API keys and OAuth tokens
workspaces/        per-workflow files written by nodes
packages/          downloaded service binaries
```

`API_KEY_ENCRYPTION_KEY` in `/opt/opencompany/.env` is the only key that can
decrypt `credentials.db`. A backup of the DB without that key is useless, and
rotating the key orphans every stored credential — there is no re-encryption
path. `bootstrap.sh` therefore never rewrites an existing `.env`.

## Operations

```bash
sudo supervisorctl status opencompany
sudo supervisorctl restart opencompany
sudo tail -f /var/log/opencompany/app.log
sudo tail -f /var/log/opencompany/error.log
curl -fsS http://127.0.0.1:<port>/health          # on the host
```
