import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

required_settings = [
    "DB_HOST",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
    "DB_PORT"
]


def get_connection():
    config = {}

    for setting in required_settings:
        value = os.getenv(setting)

        if not value:
            raise ValueError(
                f"Missing required environment variable: {setting}"
            )

        config[setting] = value

    try:
        config["DB_PORT"] = int(config["DB_PORT"])
    except ValueError:
        raise ValueError("DB_PORT must be a valid number.")

    connection = mysql.connector.connect(
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        database=config["DB_NAME"]
    )

    return connection