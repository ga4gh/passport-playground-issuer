# Passport Playground Issuer

A minimal Flask prototype of DUOS's data passport generation (`PassportResource.getDataPassport` /
`PassportService.generateDataPassport` in the Consent repo), reading dataset/DAC/DAA data from a
static JSON file instead of a database.

## Run

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python app/main.py
```

Then request a data passport by dataset identifier:

```bash
curl http://127.0.0.1:8080/api/passport/dataset/DUOS-000001
```

Sample data lives in [app/data/passport_data.json](app/data/passport_data.json) — `DUOS-000001` has
a DAC and associated DAA (returns all 4 visas), `DUOS-000002` has no DAC (returns 2 visas).

## Deploy

The [Dockerfile](Dockerfile) runs the app with gunicorn on `$PORT` (defaults to 8080), so it works
as-is on either platform below — no other config files needed.

### Render

1. Push this repo to GitHub.
2. In the Render dashboard: **New > Web Service**, connect the repo.
3. Set environment to **Docker** (Render auto-detects the `Dockerfile`) and click **Create Web Service**.

### Fly.io

```bash
fly launch    # detects the Dockerfile; accept defaults, skip Postgres/Redis
fly deploy
```

Both give you a public HTTPS URL serving `/api/passport/dataset/<dataset_identifier>`.
