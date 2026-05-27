import logging
import time
from typing import Callable

import pika
import pika.exceptions
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class TrainingRequest(BaseModel):
    solicitante_id: int
    nome_modelo: str
    #produto_treino: list[str]
    tipo_treino: str
    tabela: str
    # mapeia funções semânticas para nomes de colunas reais:
    # {"produto": "col_x", "data": "col_y", "quantidade_manha": "col_a",
    #  "quantidade_tarde": "col_b", "total": "col_c"}
    colunas: dict[str, str]
    periodos_previsao: int = 3
    #turno: str | None = None  # "MANHA" | "TARDE" | None (usa total)


class AMQPConfig(BaseModel):
    url: str
    queue: str = "modelo.treino"
    prefetch_count: int = 1
    retry_delay: int = 5
    max_retries: int = 0  # 0 = tente novamente para sempre


class AMQPConsumer:
    def __init__(self, config: AMQPConfig):
        self._config = config
        self._connection: pika.BlockingConnection | None = None
        self._channel = None

    def _connect(self) -> None:
        params = pika.URLParameters(self._config.url)
        params.heartbeat = 60
        params.blocked_connection_timeout = 300
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self._config.queue, durable=True)
        self._channel.basic_qos(prefetch_count=self._config.prefetch_count)
        logger.info("Connected to RabbitMQ, queue='%s'", self._config.queue)

    def _make_callback(self, handler: Callable[[TrainingRequest], None]):
        def callback(ch, method, _properties, body):
            try:
                request = TrainingRequest.model_validate_json(body)
                logger.info(
                    "Request received: cliente=%s produto=%s",
                    request.cliente,
                    request.produto_previsao,
                )
                handler(request)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except ValidationError as exc:
                logger.error("Invalid message schema: %s", exc)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as exc:
                logger.exception("Handler error: %s", exc)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        return callback

    def start(self, handler: Callable[[TrainingRequest], None]) -> None:
        attempts = 0
        while True:
            try:
                self._connect()
                self._channel.basic_consume(
                    queue=self._config.queue,
                    on_message_callback=self._make_callback(handler),
                )
                self._channel.start_consuming()
            except pika.exceptions.AMQPConnectionError as exc:
                attempts += 1
                if self._config.max_retries and attempts > self._config.max_retries:
                    raise
                logger.warning(
                    "Connection lost (%s). Retry %d in %ds...",
                    exc, attempts, self._config.retry_delay,
                )
                time.sleep(self._config.retry_delay)
            except KeyboardInterrupt:
                logger.info("Consumer stopped.")
                break
            finally:
                self._teardown()

    def _teardown(self) -> None:
        try:
            if self._connection and not self._connection.is_closed:
                self._connection.close()
        except Exception:
            pass
