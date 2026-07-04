import asyncio
import os
import sys
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from asyncpg import Connection
from datetime import datetime, timezone
from pydantic import ValidationError

from models import FlightChangeModel, CONSUMER_OF, ADD_SUBSCRIPTION, FLIGHT_CHANGES


def generate_error_and_exit(key, msg):
    print('error on-', key)
    print(msg)
    print('system exited')
    sys.exit(1)


async def email_sender(data, event):
    """
    Unimplemented right now.
    """
    
    print('sending email for event', event)
    await asyncio.sleep(2)
    print('email sent to - ', data)


async def consume(db: Connection):
    date_today = datetime.now(tz=timezone.utc).date()
    consumer = None
    try:
        consumer = AIOKafkaConsumer(
            *CONSUMER_OF,
            bootstrap_servers=os.environ.get('KAFKA_URL'),
            group_id=None,
            auto_offset_reset='latest'
        )
        await consumer.start()
        async for message in consumer:
            if message.topic == ADD_SUBSCRIPTION:
                await email_sender(message, ADD_SUBSCRIPTION)
            elif message.topic == FLIGHT_CHANGES:
                try:
                    flight_change=FlightChangeModel.model_validate_json(message.value)
                    data = await db.fetchval('''
                        SELECT STRING_AGG(email_id, ', ')
                        FROM subscriptions
                        WHERE flight_id = $1
                        AND "date" = $2
                    ''', str(flight_change.flight_id), date_today)
                    await email_sender(data, 'flight-change')
                except ValidationError as e:
                    print('cannot serialize this!!')
                    print(e)
    except KafkaError as e:
        generate_error_and_exit('kafka', e)
    except Exception as e:
        generate_error_and_exit('generic', e)
    finally:
        if consumer is not None:
            await consumer.stop()
