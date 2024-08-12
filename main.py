import uvicorn
from core.config import config


def main():
    uvicorn.run(
        app='app.server:app',
        host='0.0.0.0',
        port=config.port,
        workers=8
    )


if __name__ == '__main__':
    main()