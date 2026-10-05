import logging


def main() -> None:
    import uvicorn

    from backend_tu_nuevo_hogar.config import Configuracion

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = Configuracion()
    uvicorn.run("backend_tu_nuevo_hogar.app:app", host=config.host, port=config.port)
