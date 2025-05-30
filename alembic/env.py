from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.models import Base
import dotenv
import logging
# from app.config import settings

# Get logger for this module
logger = logging.getLogger(__name__)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    # return settings.DATABASE_URL
    pass # We will load settings inside the function that needs it

def run_migrations_offline() -> None:
    logger.info("Running migrations in offline mode.")
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
    logger.info("Offline migrations finished.")

def run_migrations_online() -> None:
    logger.info("Running migrations in online mode.")
    # Import and load settings here to ensure environment variables are available
    import dotenv
    dotenv.load_dotenv()
    from app.config import settings

    logger.info(f"DATABASE_URL for migrations: {settings.DATABASE_URL}")

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        logger.info("Starting migration transaction.")
        with context.begin_transaction():
            context.run_migrations()
        logger.info("Migration transaction finished.")

    logger.info("Online migrations finished.")

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 