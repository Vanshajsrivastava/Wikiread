# Wikiread

A Django-based wiki app with markdown entries stored in a relational database.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a; source .env; set +a
python manage.py migrate
python manage.py runserver
```

To import old markdown files from `entries/*.md` into DB:

```bash
python manage.py import_entries
```

## Vercel deployment

This repo includes:
- `api/index.py` (Vercel Python entrypoint)
- `vercel.json`

### Steps

1. Push this repository to GitHub.
2. Import the project in Vercel.
3. Set Environment Variables in Vercel Project Settings:
   - `SECRET_KEY`
   - `DEBUG=0`
   - `ALLOWED_HOSTS=.vercel.app`
   - `DATABASE_URL` (use Postgres; SQLite is not persistent on Vercel)
4. Deploy.

### Important

- Vercel serverless filesystem is ephemeral.
- Use Postgres in production.

## Database switching

The project reads `DATABASE_URL`.

Examples:

```bash
# SQLite (local)
export DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (recommended for production)
export DATABASE_URL=postgresql://user:password@host:5432/wikiread
```
