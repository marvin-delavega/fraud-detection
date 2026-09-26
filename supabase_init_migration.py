import os
from eventsourcing.postgres import PostgresApplicationRecorder, PostgresDatastore
from dotenv import load_dotenv

load_dotenv()

datastore = PostgresDatastore(
    dbname=os.environ["POSTGRES_DBNAME"],
    host=os.environ["POSTGRES_HOST"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    port=int(os.environ["POSTGRES_PORT"]),
    schema=os.getenv("POSTGRES_SCHEMA", "public"),

    enable_db_functions=True,

    pool_size=int(os.getenv("POSTGRES_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("POSTGRES_MAX_OVERFLOW", "10")),
    connect_timeout=float(os.getenv("POSTGRES_CONNECT_TIMEOUT", "30")),
    pre_ping=os.getenv("POSTGRES_PRE_PING", "true").lower() == "true",
    lock_timeout=int(os.getenv("POSTGRES_LOCK_TIMEOUT", "5")),
)

recorder = PostgresApplicationRecorder(datastore=datastore,
                                       events_table_name=os.getenv("EVENTS_TABLE_NAME", "stored_events"))
recorder.create_table()
print("✅ Event sourced schemas successfully deployed to Supabase!")
print("✅ PostgreSQL insert function created for fast event inserts")
