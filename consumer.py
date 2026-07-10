import asyncio
import os
import ssl
import sys
import json
import logging
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from asyncpg import Connection
from datetime import datetime, timezone
from pydantic import ValidationError

from models import FlightChangeModel, SubscriptionModel, CONSUMER_OF, ADD_SUBSCRIPTION, FLIGHT_CHANGES
from email_service import send_email
from templates import flight_change_email, subscription_confirmation_email

logger = logging.getLogger(__name__)


def generate_error_and_exit(key, msg):
    logger.critical(f'Fatal error on [{key}]: {msg}')
    sys.exit(1)


async def handle_subscription_event(message):
    """
    Handle a new subscription event — send a confirmation email
    to the subscriber.
    """
    try:
        payload = json.loads(message.value)
        subscription = SubscriptionModel.model_validate(payload)

        subject, html_body = subscription_confirmation_email(
            email_id=subscription.email_id,
            flight_id=subscription.flight_id,
            date=str(subscription.date),
        )

        success = await send_email(
            to_addresses=subscription.email_id,
            subject=subject,
            html_body=html_body,
        )

        if success:
            logger.info(f'Subscription confirmation sent to {subscription.email_id} for flight {subscription.flight_id}')
        else:
            logger.warning(f'Failed to send subscription confirmation to {subscription.email_id}')

    except (ValidationError, json.JSONDecodeError) as e:
        logger.error(f'Cannot deserialize subscription message: {e}')
    except Exception as e:
        logger.error(f'Error handling subscription event: {e}')


async def handle_flight_change_event(message, db: Connection):
    """
    Handle a flight-change event — look up all subscribers for the
    affected flight and send each an update email.
    """
    #print('recieved ')
    try:
        flight_change = FlightChangeModel.model_validate_json(message.value)
        date_today = datetime.now(tz=timezone.utc).date()

        # Fetch comma-separated subscriber emails for this flight + date
        subscriber_emails = await db.fetchval('''
            SELECT STRING_AGG(email_id, ', ')
            FROM subscriptions
            WHERE flight_id = $1
            AND "date" = $2
        ''', flight_change.flight_id, date_today)

        if not subscriber_emails:
            print(f'No subscribers for flight {flight_change.flight_id} on {date_today}')
            logger.debug(f'No subscribers for flight {flight_change.flight_id} on {date_today}')
            return

        subject, html_body = flight_change_email(
            flight_id=flight_change.flight_id,
            parameter=flight_change.parameter,
            old_value=flight_change.old_value,
            new_value=flight_change.new_value,
            modified_at=flight_change.modified_at,
        )

        success = await send_email(
            to_addresses=subscriber_emails,
            subject=subject,
            html_body=html_body,
        )

        if success:
            logger.info(
                f'Flight change email sent for flight {flight_change.flight_id} '
                f'({flight_change.parameter}: {flight_change.old_value} → {flight_change.new_value}) '
                f'to [{subscriber_emails}]'
            )
        else:
            logger.warning(f'Failed to send flight change email for flight {flight_change.flight_id}')

    except ValidationError as e:
        logger.error(f'Cannot deserialize flight-change message: {e}')
    except Exception as e:
        logger.error(f'Error handling flight change event: {e}')


async def consume(db: Connection):
    consumer = None
    try:
        ca_cert_path = os.environ.get('KAFKA_CA_CERT', 'certs/ca.pem')
        ssl_context = ssl.create_default_context(cafile=ca_cert_path)
        consumer = AIOKafkaConsumer(
            *CONSUMER_OF,
            bootstrap_servers=os.environ.get('KAFKA_URL'),
            group_id=None,
            auto_offset_reset='latest',
            security_protocol='SASL_SSL',
            sasl_mechanism='PLAIN',
            sasl_plain_username=os.environ.get('KAFKA_USERNAME'),
            sasl_plain_password=os.environ.get('KAFKA_PASSWORD'),
            ssl_context=ssl_context,
        )
        await consumer.start()
        logger.info(f'Kafka consumer started — listening on topics: {CONSUMER_OF}')

        async for message in consumer:
            logger.debug(f'Received message on topic: {message.topic}')

            if message.topic == ADD_SUBSCRIPTION:
                await handle_subscription_event(message)
            elif message.topic == FLIGHT_CHANGES:
                await handle_flight_change_event(message, db)

    except KafkaError as e:
        generate_error_and_exit('kafka', e)
    except Exception as e:
        generate_error_and_exit('generic', e)
    finally:
        if consumer is not None:
            await consumer.stop()
            logger.info('Kafka consumer stopped')
