import os
import time

import pymysql


def main() -> None:
    host = os.getenv("MYSQL_HOST", "mysql")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "pet")
    password = os.getenv("MYSQL_PASSWORD", "pet123456")
    database = os.getenv("MYSQL_DATABASE", "pet_planet")
    timeout_seconds = int(os.getenv("MYSQL_WAIT_TIMEOUT", "120"))
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=3,
            )
            connection.close()
            print("mysql ready")
            return
        except Exception as exc:
            last_error = exc
            print(f"waiting for mysql: {exc}")
            time.sleep(2)

    raise SystemExit(f"mysql is not ready: {last_error}")


if __name__ == "__main__":
    main()
