from __future__ import with_statement
from logging.config import fileConfig
from flask import current_app
from alembic import context

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(context.config.config_file_name)

# Access the Flask app's SQLAlchemy configuration.
config = context.config
target_metadata = current_app.extensions['migrate'].db.metadata


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    This configures the context with just a URL.
    """
    context.configure(
        url=current_app.config.get('SQLALCHEMY_DATABASE_URI'),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.
    Connect to the database and apply migrations.
    """
    connectable = current_app.extensions['migrate'].db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
