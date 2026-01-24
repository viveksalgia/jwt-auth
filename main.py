import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI

from app.utils.settings import settings
from app.utils.schema import StatusResponse

from app.users import manage_users
from app.jwt import jwt_token

logging.basicConfig(level=settings.log_level, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auth",
    description="Auth Project",
    version="1.0.0",
)

app.include_router(manage_users.router)
app.include_router(jwt_token.router)

@app.get("/", response_model=StatusResponse, summary="Health Check")
async def health_check() -> dict[str, Any]:
    """
    Returns the operational status and current timestamp of the API.
    """
    return {"status": "ok", "datetime": str(datetime.now())}