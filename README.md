# Email Service

A lightweight email-sender microservice for the **flight-tracker** application.

## What it does

This service runs as a standalone Kafka consumer. It listens to subscription and flight-change topics, queries PostgreSQL for affected subscribers, and dispatches email notifications via SMTP.

**Flow:** Kafka message → validate & look up subscribers → render HTML template → send email via SMTP

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│    Kafka      │────▸│  consumer.py     │────▸│  SMTP Server │
│  (topics)     │     │  (event router)  │     │  (email out) │
└──────────────┘     └────────┬─────────┘     └──────────────┘
                              │
                     ┌────────┴─────────┐
                     │   PostgreSQL     │
                     │  (subscribers)   │
                     └──────────────────┘
```

## Modules

| File               | Purpose                                                    |
| ------------------- | ---------------------------------------------------------- |
| `main.py`           | Entry point — connects to PostgreSQL and starts consuming  |
| `consumer.py`       | Kafka consumer — routes messages to handlers               |
| `email_service.py`  | Async SMTP sender via `aiosmtplib`                         |
| `templates.py`      | HTML email templates for notifications                     |
| `models.py`         | Pydantic models & Kafka topic constants                    |

## Consumer

The consumer subscribes to two Kafka topics:

- **`subscriptions`** — triggered when a user subscribes to a flight; sends a confirmation email.
- **`flight-changes`** — triggered when a tracked flight has updates; queries PostgreSQL for all subscribers of that flight and notifies them via email.

## Why not FastAPI?

This service has no REST API surface — it only consumes Kafka events and sends emails. Pulling in FastAPI (and an HTTP server) would add unnecessary overhead for a process that just needs an async event loop reading from a message broker.

## Setup

1. Create a `.env` file in the project root (see `.env.example`):

```env
# Database
DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/<db>"

# Kafka
KAFKA_URL="<kafka-broker-host>:<port>"
KAFKA_USERNAME=
KAFKA_PASSWORD=

# SMTP (use your provider's settings)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=Flight Tracker
SMTP_FROM_EMAIL=noreply@yourapp.com
SMTP_USE_TLS=true
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python3 main.py
```
