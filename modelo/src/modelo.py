import logging
import os

from models.cloudAMQP import AMQPConfig, AMQPConsumer, TrainingRequest
from models.model import DatabaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

AMQP_URL = os.environ["AMQP_URL"]
DB_DSN = os.environ["DB_DSN"]
AMQP_QUEUE = os.environ.get("AMQP_QUEUE", "modelo.treino")


def handle_request(request: TrainingRequest) -> None:
    db = DatabaseModel(dsn=DB_DSN)
    try:
        db.connect()
        df = db.fetch_product_history(
            tabela=request.tabela,
            colunas=request.colunas,
            produtos=request.produto_treino,
        )
        logger.info(
            "Buscado %d linhas para cliente=%s tabela=%s",
            len(df),
            request.cliente,
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
