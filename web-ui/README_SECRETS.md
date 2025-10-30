# Secrets Manager (Web UI)

- Set API base for local dev:

`export NEXT_PUBLIC_API_BASE=http://localhost:8002`

- Pages:
  - `/secrets` — list, create, rotate, delete.

- Server ENV (configure as needed):
  - `SECRETS_ENCRYPTION_KEY` (Fernet base64 key)
  - `VAULT_ADDR`, `VAULT_TOKEN`
  - `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
  - `GCP_PROJECT`
