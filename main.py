from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import event_router, payment_router, health_router
from app.application import PaymentApplication

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):

    payment_app = PaymentApplication()

    app.state.main_app = payment_app

    import app.state as state_module
    state_module.main_app = payment_app
    yield

    if app.state.main_app:
        app.state.main_app.close()
    app.state.main_app = None
    state_module.main_app = None

app = FastAPI(lifespan=lifespan)
app.include_router(event_router)
app.include_router(payment_router)
app.include_router(health_router)
