# STRIX Telegram Persistent Lab Service

Service unit: `deploy/systemd/strix-telegram-lab.service`

Purpose: run the STRIX/Saga Fusion Telegram lab poller continuously for `@RadamanthysCyberBot` in controlled, evidence-only lab mode.

## Safety envelope

The service preserves the existing Telegram lab constraints:

- Telegram token is loaded from environment only (`%h/.ductor/.env` by default in the user service).
- Polling mode only: `TELEGRAM_POLLING_ENABLED=true`, `TELEGRAM_WEBHOOK_ENABLED=false`.
- Allowlist required via `TELEGRAM_ALLOWED_USER_IDS`.
- No real LLM, CloudOps, pentest, malware/payload/webshell, attachment execution, or destructive command execution.
- Responses remain lab/evidence-only: `execution_allowed=false`, `executed=false`, `non_authoritative=true`, `evidence_required=true`, `report_required=true`.
- Logs are redacted by the runtime; do not add secrets to the unit file or command line.
- `Restart=on-failure` lets systemd restart the poller after failures.

## Install/start as a user service

From `/mnt/Proyectos/strix_core_fusion`:

```bash
mkdir -p ~/.config/systemd/user
cp deploy/systemd/strix-telegram-lab.service ~/.config/systemd/user/strix-telegram-lab.service
systemctl --user daemon-reload
systemctl --user enable --now strix-telegram-lab.service
systemctl --user status strix-telegram-lab.service --no-pager
journalctl --user -u strix-telegram-lab.service -n 50 --no-pager
```

Optional, if the service should survive logout on a normal Linux host:

```bash
loginctl enable-linger "$USER"
```

## Runtime command

The service runs:

```bash
/usr/bin/python3 -m saga_fusion.telegram.telegram_lab_runtime \
  --service \
  --poll-timeout-seconds 15 \
  --start-at-latest
```

`--service` is persistent and ignores bounded `--max-messages`/`--max-seconds` options. For smoke tests, keep bounded mode:

```bash
python3 -m saga_fusion.telegram.telegram_lab_runtime \
  --max-messages 2 \
  --max-seconds 120 \
  --poll-timeout-seconds 15 \
  --start-at-latest
```

## Duplicate-poller guard

Before starting a live service, check for an existing poller for the same token:

```bash
pgrep -af 'saga_fusion.telegram.telegram_lab_runtime|strix-telegram-lab'
```

Do not run multiple pollers against the same Telegram bot token.
