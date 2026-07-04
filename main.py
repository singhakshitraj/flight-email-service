import asyncpg
import asyncio
import os
from dotenv import load_dotenv
from consumer import consume, generate_error_and_exit

load_dotenv()

async def create_connection():
    try:
        conn = await asyncpg.connect(os.environ.get('DATABASE_URL'))
        return conn
    except (ConnectionError, OSError) as e:
        generate_error_and_exit('db-connection', e)


async def main():
    connection = await create_connection()
    await consume(connection)


if __name__ == "__main__":
    asyncio.run(main())
