import asyncpg
import asyncio
import os
import logging
from dotenv import load_dotenv
from consumer import consume, generate_error_and_exit

load_dotenv()

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def create_connection():
    try:
        conn = await asyncpg.connect(os.environ.get('DATABASE_URL'))
        logger.info("Connected to PostgreSQL")
        return conn
    except (ConnectionError, OSError) as e:
        generate_error_and_exit('db-connection', e)


async def main():
    logger.info("Starting email service...")
    connection = await create_connection()
    await consume(connection)


if __name__ == "__main__":
    asyncio.run(main())
