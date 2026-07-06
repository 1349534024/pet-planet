import json
import uuid
from datetime import datetime, timezone
from typing import Any

import pika

from app.core.config import settings

EVENT_EXCHANGE = "petplanet.events"


def build_event(event_type: str, source: str, data: dict[str, Any], trace_id: str | None = None) -> dict[str, Any]:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "data": data,
        "trace_id": trace_id or str(uuid.uuid4()),
    }


def publish_event(routing_key: str, event: dict[str, Any]) -> None:
    parameters = pika.URLParameters(settings.rabbitmq_url)
    connection = pika.BlockingConnection(parameters)
    try:
        channel = connection.channel()
        channel.exchange_declare(exchange=EVENT_EXCHANGE, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=EVENT_EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(event, ensure_ascii=False).encode("utf-8"),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
    finally:
        connection.close()
