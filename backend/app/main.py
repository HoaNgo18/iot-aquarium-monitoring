from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.mqtt_consumer import MqttConsumer
from app.realtime import RealtimeHub


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def create_app(start_background_services: bool = True) -> FastAPI:
    settings = get_settings()
    realtime_hub = RealtimeHub()
    consumer = MqttConsumer(settings, realtime_hub.publish_from_thread)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        realtime_hub.bind_running_loop()
        if start_background_services:
            consumer.start()
        try:
            yield
        finally:
            if start_background_services:
                consumer.stop()
            realtime_hub.unbind_loop()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    application.state.mqtt_consumer = consumer
    application.state.realtime_hub = realtime_hub
    application.include_router(api_router)
    return application


app = create_app()
