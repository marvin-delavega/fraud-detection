"""Shared application state - avoids circular imports."""
from app.application import PaymentApplication
from fastapi import FastAPI

# This will be set on app.state by main.py lifespan
main_app: PaymentApplication | None = None