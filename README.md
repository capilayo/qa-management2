# QA Management System

A Flask + IBM Cloudant web app for managing QA team availability and users.

## Features
- **Dashboard** — live QA availability board (status counts + agent cards)
- **QA Availability** — click any card to update status and current task
- **User Management** — add or remove team members

## Stack
- **Backend**: Python / Flask REST API
- **Database**: IBM Cloudant (NoSQL)
- **Frontend**: Single-page HTML/JS app served by Flask

## Environment Variables

| Variable | Description |
|---|---|
| `CLOUDANT_URL` | IBM Cloudant instance URL |
| `CLOUDANT_APIKEY` | IAM API key (preferred) |
| `CLOUDANT_USERNAME` | Legacy username (alternative) |
| `CLOUDANT_PASSWORD` | Legacy password (alternative) |

## Local Development

```bash
pip install -r requirements.txt
# create a .env file with your Cloudant credentials
python start.py
```

Open http://localhost:5052

## Deploy to Render

1. Connect this repo in Render
2. Set `CLOUDANT_URL` and `CLOUDANT_APIKEY` environment variables
3. Deploy — the app will auto-seed the database on first run
