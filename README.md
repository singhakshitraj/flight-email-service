# Email Service

A lightweight email-sender microservice for the **flight-tracker** application.

## What it does

This service runs as a standalone Kafka consumer. It listens to subscription and flight-change topics, queries PostgreSQL for affected subscribers, and dispatches email notifications accordingly.

**Flow:** Kafka message → validate & look up subscribers → send email

## Consumer

The consumer subscribes to two Kafka topics:

- **`add-subscription`** — triggered when a user subscribes to a flight; sends a confirmation email.
- **`flight-changes`** — triggered when a tracked flight has updates; queries PostgreSQL for all subscribers of that flight and notifies them via email.

## Why not FastAPI?

This service has no REST API surface — it only consumes Kafka events and sends emails. Pulling in FastAPI (and an HTTP server) would add unnecessary overhead for a process that just needs an async event loop reading from a message broker.

## Setup

Create a `.env` file in the project root with the following variables:

```env
DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/<db>"
KAFKA_URL="<kafka-broker-host>:<port>"
```

## Run

```bash
.venv/bin/python3 main.py
```
