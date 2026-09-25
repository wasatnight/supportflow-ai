import os

import uvicorn


def main() -> None:
    os.environ.setdefault(
        "DATABASE_MODE",
        "sqlite",
    )

    from app.main import app

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()
