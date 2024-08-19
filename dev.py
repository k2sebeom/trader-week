import uvicorn
from core.config import config


def main():
    uvicorn.run(
        app="app.server:app",
        host="127.0.0.1",
        port=config.port,
        reload=True,
        workers=1,
    )


if __name__ == "__main__":
    main()
