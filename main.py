import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI
from urllib.parse import urlencode

from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.utils.settings import settings
from app.utils.schema import StatusResponse

from app.users import manage_users
from app.jwt import jwt_token
import base64

logging.basicConfig(level=settings.log_level, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auth",
    description="Auth Project",
    version="1.0.0",
)

app.include_router(manage_users.router)
app.include_router(jwt_token.router)

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_model=StatusResponse, summary="Health Check")
async def health_check() -> dict[str, Any]:
    """
    Returns the operational status and current timestamp of the API.
    """
    return {"status": "ok", "datetime": str(datetime.now())}

@app.get("/login", summary="Login Page")
async def login_page(request: Request) -> HTMLResponse:
    """
    Returns the operational status and current timestamp of the API.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", summary="Register Page")
async def register_page(request: Request) -> HTMLResponse:
    """
    Returns the operational status and current timestamp of the API.
    """
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/return", summary="Callback Page")
async def callback_page(request: Request) -> HTMLResponse:
    """
    Returns the operational status and current timestamp of the API.
    """
    basic_auth = request.headers.get("Authorization").split(" ")[1]
    basic_auth = base64.b64decode(basic_auth).decode('utf-8')
    data = await request.json()
    state = data.get("state")
    # The client app says where to send the browser back; only allow URLs we know (prevents open redirects).
    redirect_uri = data.get("redirect_uri") or settings.allowed_redirect_uris[0]
    if redirect_uri not in settings.allowed_redirect_uris:
        return JSONResponse({"error": "redirect_uri is not allowed"}, status_code=400)
    if not basic_auth:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Missing Authorization header"})
    else:
        username = basic_auth.split(":")[0]
        password = basic_auth.split(":")[1]
        class RequestBody:
            def __init__(self, body):
                self.body = body
                self.status_code = 202
        request_body = RequestBody(b'{"username": "' + username.encode() + b'", "password": "' + password.encode() + b'"}')
        response = await jwt_token.login_for_access_token(user_data=request_body)
        token = response.access_token
    # Return the URL instead of redirecting: the login page calls this with fetch(), which would follow a 303 itself
    # (without the browser's cookies). The page must navigate the browser to this URL.
    query = urlencode({"access_token": token, "state": state})
    separator = "&" if "?" in redirect_uri else "?"
    return JSONResponse({"redirect_url": f"{redirect_uri}{separator}{query}"})