import os


class BotSettings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    REDIS_HOST = os.getenv("REDIS_HOST")
    KAFKA_HOST = os.getenv("KAFKA_HOST")
    KAFKA_PORT = os.getenv("KAFKA_PORT")
