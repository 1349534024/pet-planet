from logging.config import fileConfig
from importlib import import_module
from pkgutil import iter_modules

from alembic import context
from alembic.ddl.impl import DefaultImpl
from sqlalchemy import engine_from_config, pool
from sqlalchemy import Column, MetaData, PrimaryKeyConstraint, String, Table

from app.core.config import settings
from app.db.base import Base
import app.models

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def import_model_modules() -> None:
    for module_info in iter_modules(app.models.__path__):
        if not module_info.ispkg:
            import_module(f"{app.models.__name__}.{module_info.name}")


import_model_modules()
target_metadata = Base.metadata


def version_table_impl(
    self: DefaultImpl,
    *,
    version_table: str,
    version_table_schema: str | None,
    version_table_pk: bool,
    **kw: object,
) -> Table:
    version_table_obj = Table(
        version_table,
        MetaData(),
        Column("version_num", String(64), nullable=False),
        schema=version_table_schema,
    )
    if version_table_pk:
        version_table_obj.append_constraint(
            PrimaryKeyConstraint("version_num", name=f"{version_table}_pkc")
        )

    return version_table_obj


DefaultImpl.version_table_impl = version_table_impl


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
