import logging
import os

from db.connection import DatabaseConnection
from messaging.cloudamqp import AMQPConfig, AMQPConsumer, TrainingRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

AMQP_URL = os.environ["AMQP_URL"]
DB_DSN = os.environ["DB_DSN"]
AMQP_QUEUE = os.environ.get("AMQP_QUEUE", "modelo.treino")


def handle_request(request: TrainingRequest) -> None:
    db = DatabaseConnection(dsn=DB_DSN)
    try:
        db.connect()
        df = db.tabela_dinamica.fetch_product_history(
            tabela=request.tabela,
            colunas=request.colunas,
            produtos=request.produto_treino,
        )
        logger.info(
            "Buscado %d linhas para modelo_id=%s tabela=%s",
            len(df),
            request.modelo_id,
            request.tabela,
        )
        # TODO: treinar modelo e entregar o resultado da previsão
    finally:
        db.close()


def main() -> None:
    config = AMQPConfig(url=AMQP_URL, queue=AMQP_QUEUE)
    consumer = AMQPConsumer(config)
    logger.info("Starting modelo service...")
    consumer.start(handle_request)


if __name__ == "__main__":
    main()
