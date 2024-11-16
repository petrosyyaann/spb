from .base import clickhouse_session
from traceback import format_exc
from settings import settings
import logging


def create_tables():
    client = None
    try:
        client = clickhouse_session()
        # Create database
        client.query(f"CREATE DATABASE IF NOT EXISTS {settings.CLICKHOUSE_DB_NAME}")
        # Switch to the specified database
        client.query(f"USE {settings.CLICKHOUSE_DB_NAME}")
        # Create `users` table if it does not exist
        client.query("""
            CREATE TABLE IF NOT EXISTS history
            (
                entity_id UInt32,
                history_property_name Nullable(String),
                history_date Datetime,
                history_version int,
                history_change_type Nullable(Enum('FIELD_CHANGED', 'CREATED')),
                history_change Nullable(String)
            ) ENGINE = MergeTree()
            ORDER BY entity_id;
        """)

        client.query("""
            CREATE TABLE IF NOT EXISTS entity (
                entity_id int,
                area Nullable(String),
                type Nullable(Enum8('Дефект','История','Задача','Подзадача')),
                status Nullable(Enum8('Закрыто','Тестирование','Отклонен исполнителем','Исправление','Анализ','Создано','Выполнено','Отложен','В работе','Готово к разработке','СТ','Подтверждение исправления','Разработка','Подтверждение','СТ Завершено','Локализация','В ожидании')),
                state Nullable(Enum8('Normal')),
                priority Nullable(Enum8('Средний','Критический','Высокий','Низкий')),
                ticket_number Nullable(String),
                name Nullable(String),
                create_date Nullable(datetime),
                created_by Nullable(String),
                update_date Nullable(datetime),
                updated_by Nullable(String),
                parent_ticket_id Nullable(int),
                assignee Nullable(String),
                owner Nullable(String),
                due_date Nullable(date),
                rank Nullable(String),
                estimation Nullable(int),
                spent Nullable(int),
                workgroup Nullable(String),
                resolution Nullable(Enum8('Готово','nan','Отклонено','Отменен инициатором','Дубликат'))
            ) ENGINE = MergeTree()
            ORDER BY entity_id
        """)

    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        # logging.error(format_exc())
        raise e
    finally:
        if client is not None:
            client.close()
