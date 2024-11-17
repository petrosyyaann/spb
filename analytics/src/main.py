# from torni_analytics.core.rabbitmq import rabbit_connection
import aio_pika
import asyncio
import logging
from model import CSVs, Sprint
import polars as pl
import numpy as np
from enum import IntEnum

from pl_utils import get_lf
from settings import settings
from session import with_database

logging.getLogger().setLevel(logging.INFO)


class Feature(IntEnum):
    to_do_estimation = 0
    processed_estimation = 1
    done_estimation = 2
    removed_estimation = 3
    blocked_tasks_estimation = 4
    created_tasks_estimation = 5
    excluded_tasks_estimation = 6
    created_tasks_amount = 7
    excluded_tasks_amount = 8


async def main(loop):
    connection = await aio_pika.connect_robust(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASS,
        loop=loop
    )

    async with connection:
        channel: aio_pika.abc.AbstractChannel = await connection.channel()
        queue_read: aio_pika.abc.AbstractQueue = await channel.declare_queue(
            "csv",
            durable=True
        )
        exchange_write = await channel.declare_exchange("sprint_processed", type=aio_pika.exchange.ExchangeType.FANOUT)
        with with_database() as db:
            async with queue_read.iterator() as queue_iter:
                async for message in queue_iter:
                    # async with message.process():

                    csvs = CSVs.model_validate_json(message.body.decode())
                    logging.info(f"Received new CSVs:{csvs}")

                    entities = get_lf(csvs.entities_s3).filter(
                        pl.col("entity_id").is_not_null()).select(
                        "entity_id", "area", "type", "status", "priority", "ticket_number", "name",
                        "estimation").collect()

                    sprints = get_lf("data/sprints-Table 1.csv").filter(pl.col("sprint_name").is_not_null()).select(
                        "sprint_name", "sprint_start_date", "entity_ids").with_columns(
                        pl.col("sprint_start_date").str.to_datetime().dt.timestamp("ms") // 86400000).collect()

                    tasks = sprints.with_columns(
                        pl.col("entity_ids").str.strip_chars(r'{}').str.split(",").alias("entity_id"))
                    t = tasks.with_columns(pl.col("entity_id").list.len())
                    all_task_in_sprint = dict(zip(t["sprint_name"].to_list(), t["entity_id"].to_list()))

                    tasks = tasks.explode("entity_id").with_columns(pl.col("entity_id").cast(pl.Int64, strict=False))
                    all_tasks_estimations = entities.select("entity_id", "estimation").join(
                        tasks.select("entity_id", "sprint_name"), on="entity_id").group_by("sprint_name").agg(
                        pl.col("estimation").sum())

                    all_tasks_estimations = dict(zip(all_tasks_estimations["sprint_name"].to_list(), t["estimation"].to_list()))

                    sprints = {k: (i, v) for i, (k, v) in
                               enumerate(zip(sprints["sprint_name"].to_list(), sprints["sprint_start_date"].to_list()))}

                    ticket2id = dict(zip(entities["ticket_number"].to_list(), entities["entity_id"].to_list()))

                    entities = entities.select("entity_id", "area", "type", "status", "priority", "name",
                                               "estimation").with_columns(
                        pl.col('status').replace_strict(
                            ['Создано', 'Закрыто', 'Выполнено', 'Отклонен исполнителем'],
                            [0, 2, 2, 2], default=1, return_dtype=pl.Int8)).with_columns(
                        pl.col('type').replace_strict(
                            ['Дефект'],
                            [1], default=0, return_dtype=pl.Int8)
                    ).with_columns(pl.col("estimation").fill_null(0))
                    entities.with_columns(pl.lit(0).alias("status"))

                    state2int = {"created": 0, "closed": 2, "done": 2, "rejectedByThePerformer": 2}
                    entities = {k: list(v[0]) + ["", "", 0] for k, v in entities.rows_by_key("entity_id").items()}

                    history = get_lf("data/history-Table 1.csv").filter(
                        pl.col("entity_id").is_not_null()
                        & pl.col("history_property_name").is_not_null()
                        & pl.col("history_property_name").is_in(["Статус", "Резолюция", "Спринт", "Связанные Задачи"])
                    ).select(
                        "entity_id", "history_property_name", "history_date", "history_change").collect()
                    history = history.with_columns(
                        pl.col("history_date").str.to_datetime('%m/%d/%y %H:%M', time_unit="ms",
                                                               strict=False)).with_columns(
                        pl.col("history_change").str.split(" -> ").list.last()).sort(
                        'history_date', maintain_order=True).with_columns(
                        pl.col('history_change').shift(1).alias('history_change_prev')).with_columns(
                        pl.col('entity_id').shift(1).alias('entity_id_prev')).with_columns(
                        (pl.col("history_date").dt.timestamp("ms") // 86400000).alias("day"))

                    day_features = np.zeros((len(sprints), 14, len(Feature._member_names_)))

                    for (day,), df in history.group_by("day", maintain_order=True):
                        df = df.with_columns(
                            history_property_name=pl.when(pl.col("history_property_name") == "Статус").then(
                                pl.col("history_change").replace_strict(
                                    ['created', 'closed', 'done', 'rejectedByThePerformer'],
                                    ['0', '2', '2', '2'], default='1', return_dtype=pl.String)
                            ).otherwise(
                                pl.col("history_property_name")
                            )
                        )
                        df = df.group_by(["entity_id", "history_property_name"], maintain_order=True).last()
                        for row in df.iter_rows():
                            ent_id = row[0]
                            if ent_id not in entities:
                                continue
                            ent = entities[ent_id]
                            sprint_name = ent[7]
                            sprint = sprints.get(sprint_name, None)
                            day_offset = 15
                            sprint_id = -1
                            if sprint is not None:
                                sprint_id = sprint[0]
                                day_offset = sprint[1] - day
                                if day_offset < 0:
                                    day_offset = 0
                            # print(row)
                            match row[1]:
                                case "Резолюция":
                                    entities[ent_id][6] = row[3]
                                case "0":
                                    print(row)
                                    ent[2] = 0
                                    if sprint_id != -1 and day_offset < 14:
                                        day_features[sprint_id, day_offset, Feature.to_do_estimation] += ent[5]
                                case "1":
                                    ent[2] = 1
                                    if sprint_id != -1 and day_offset < 14:
                                        day_features[sprint_id, day_offset, Feature.processed_estimation] += ent[5]
                                case "2":
                                    ent[2] = 2
                                    if sprint_id != -1 and day_offset < 14:
                                        if ent[6] in ['Отклонено', 'Дубликат', 'Отменен инициатором']:
                                            day_features[sprint_id, day_offset, Feature.removed_estimation] += ent[5]
                                        else:
                                            day_features[sprint_id, day_offset, Feature.done_estimation] += ent[5]
                                case "Спринт":
                                    new_sprint_name = row[3]

                                    old_sprint_name = ent[7]
                                    ent[7] = new_sprint_name
                                    new_sprint = sprints.get(new_sprint_name, None)
                                    old_sprint = sprints.get(old_sprint_name, None)
                                    if new_sprint:
                                        day_offset = new_sprint[1] - day
                                        sprint_id = new_sprint[0]
                                        if day_offset < 0:
                                            day_offset = 0
                                        if day_offset < 14:
                                            day_features[sprint_id, day_offset, Feature.created_tasks_estimation] += \
                                            ent[5]
                                            day_features[sprint_id, day_offset, Feature.created_tasks_amount] += 1
                                            match ent[2]:
                                                case 0:
                                                    day_features[sprint_id, day_offset, Feature.to_do_estimation] += \
                                                    ent[5]
                                                case 1:
                                                    day_features[sprint_id, day_offset, Feature.processed_estimation] += \
                                                        ent[5]
                                                case 2:
                                                    if ent[6] in ['Отклонено', 'Дубликат', 'Отменен инициатором']:
                                                        day_features[
                                                            sprint_id, day_offset, Feature.removed_estimation] += \
                                                            ent[5]
                                                    else:
                                                        day_features[sprint_id, day_offset, Feature.done_estimation] += \
                                                        ent[
                                                            5]

                                            day_features[sprint_id, day_offset, Feature.created_tasks_amount] += 1

                                            if ent[8] != 0:
                                                blocked_by = entities.get(ent[8], None)
                                                if blocked_by and blocked_by[2] != 2:
                                                    day_features[
                                                        sprint_id, day_offset, Feature.blocked_tasks_estimation] += \
                                                        blocked_by[5]

                                    if old_sprint:
                                        day_offset = old_sprint[1] - day
                                        sprint_id = old_sprint[0]
                                        if day_offset < 0:
                                            day_offset = 0
                                        if day_offset < 14:
                                            # print(f"remove from {sprint_id} at day {day_offset}")
                                            day_features[sprint_id, day_offset, Feature.excluded_tasks_estimation] += \
                                            ent[5]
                                            day_features[sprint_id, day_offset, Feature.excluded_tasks_amount] += 1
                                case 'Связанные Задачи':
                                    if row[3] == "":
                                        ent[8] = 0
                                    else:
                                        if row[4] == "isBlockedBy":
                                            blocked_by_id = ticket2id.get(row[3], 0)
                                            ent[8] = blocked_by_id
                                            blocked_by = entities.get(blocked_by_id, None)
                                            if blocked_by and blocked_by[3] != 2:
                                                sprint_name = ent[7]
                                                sprint = sprints.get(sprint_name, None)
                                                if sprint is not None:
                                                    sprint_id = sprint[0]
                                                    day_offset = sprint[1] - day
                                                    if day_offset < 0:
                                                        day_offset = 0
                                                    elif day_offset > 13:
                                                        continue
                                                    day_features[
                                                        sprint_id, day_offset, Feature.blocked_tasks_estimation] += \
                                                        blocked_by[5]
                    result = []
                    for name, (i, d) in sprints:
                        result.append(Sprint(name=name, status="",
                               to_do_estimation_points=day_features[i, :, Feature.to_do_estimation].tolist(),
                               processed_estimation_points=day_features[i,:,Feature.processed_estimation].tolist(),
                               removed_estimation_points=day_features[i,:,Feature.removed_estimation].tolist(),
                               done_estimation_points = day_features[i, :, Feature.done_estimation].tolist(),
                               blocked_tasks_points = day_features[i, :, Feature.blocked_tasks_estimation].tolist(),
                               created_tasks_amount=day_features[i, :, Feature.created_tasks_amount].tolist(),
                               created_tasks_points=day_features[i, :, Feature.created_tasks_estimation].tolist(),
                               excluded_tasks_amount=day_features[i, :, Feature.excluded_tasks_amount].tolist(),
                               excluded_tasks_points=day_features[i, :, Feature.excluded_tasks_estimation].tolist(),
                               tasks_in_sprint=all_task_in_sprint.get(name,10),
                               all_tasks_estimation=all_tasks_estimations.get(name,10),
                               to_do_estimation=day_features[i, :, Feature.to_do_estimation].sum(),
                               done_estimation=day_features[i, :, Feature.done_estimation].tolist(),

                               processed_estimation=day_features[i, :, Feature.processed_estimation].tolist(),
                               removed_estimation=day_features[i, :, Feature.removed_estimation].tolist(),
                               blocked_tasks=day_features[i, :, Feature.blocked_tasks_estimation].tolist(),
                               created_tasks=day_features[i, :, Feature.created_tasks_estimation].tolist(),
                               excluded_tasks=day_features[i, :, Feature.excluded_tasks_estimation].tolist(),
                        ))
                    db.add_all(result)
                    db.commit()
                    await message.ack()


if __name__ == "__main__":
    # asyncio.run(main())
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
