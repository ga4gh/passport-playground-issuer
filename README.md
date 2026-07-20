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
