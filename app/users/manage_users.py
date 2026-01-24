from app.utils.settings import settings
from app.utils.schema import Users, StatusResponse, CheckUserName

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime

import logging
import uuid
import json
import base64

logging.basicConfig(level=settings.log_level, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users/v1")


@router.post("/register", summary="Create a user in database")
async def create_user(request: Users) -> JSONResponse:

    response = validate_username(request.username)

    if response.status_code != 0:
        return JSONResponse(content=StatusResponse(status = 'Error, Username already exists', datetime = str(datetime.now())).__dict__,
                            status_code = 400)
    
    try:
        logger.info("Get Database Object")
        conn = settings.get_mariadb_cursor()
        cur = conn.cursor()

        query = f"INSERT INTO users(USER_UUID, USERNAME, PASSWORD, EMAIL_ADDRESS, FIRST_NAME, MIDDLE_NAME, LAST_NAME) \
                  VALUES('{uuid.uuid4()}', '{request.username}', '{settings.passwordhash.hash(request.password)}', '{request.email_address}', \
                    '{request.first_name}', '{request.middle_name}', '{request.last_name}')"

        logger.info(f"Query - {query}")

        cur.execute(query)
        conn.commit()

        ret_resp = StatusResponse(status = 'Success', datetime = str(datetime.now()))

        return JSONResponse(content=ret_resp.__dict__, status_code=201)
    
    except Exception as e:
        logger.exception(f"Exception occurred - {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

def validate_username(username: str) -> CheckUserName:
    try:
        logger.info("Get Database Object")
        count = 0
        conn = settings.get_mariadb_cursor()
        cur = conn.cursor()

        query = f"select count(1) from users where username = '{username}'"

        logger.info(f"Query - {query}")

        cur.execute(query)
        conn.commit()

        for i in cur:
            count = i[0]

        return CheckUserName(status_code=count, message="Username is available")
    
    except Exception as e:
        logger.exception(f"Exception occurred - {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

@router.get("/getusers", response_model=Users, summary="Gets a user from database")
async def get_user_details(username: str=None) -> JSONResponse:
    
    logger.info(f"Username is {username}")

    if username is not None:
        response = validate_username(username)

        if response.status_code == 0:
            return JSONResponse(content=StatusResponse(status = 'User does not exists. Please check the username in URL parameters', datetime = str(datetime.now())).__dict__,
                                status_code = 400)
    
    try:
        logger.info("Get Database Object")
        conn = settings.get_mariadb_cursor()
        cur = conn.cursor()
        users: list[Users.__dict__] = []
        
        if username is not None:
            query = f"select * from users where username = '{username}'"
        else:
            query = "select * from users"
        
        logger.info(f"Query - {query}")

        cur.execute(query)
        conn.commit()

        for resp in cur:
            user = Users(username=resp[2], first_name=None, last_name=None)
            user.user_id = resp[0]
            user.user_uuid = resp[1]
            user.username = resp[2]
            user.password = resp[3]
            user.email_address = resp[4]
            user.first_name = resp[5]
            user.middle_name = resp[6]
            user.last_name = resp[7]

            users.append(user.__dict__)


        return JSONResponse(content=users, status_code=200)
    
    except Exception as e:
        logger.exception(f"Exception occurred - {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

@router.post("/validate", response_model=Users, summary="Validates a user password from database. Input credentials are username:password with b64 encoding")
async def validate_password(request: Request) -> JSONResponse:
    auth_header = request.headers.get("Authorization")
    credentials = auth_header.split(" ")[1]
    creds = base64.b64decode(credentials).decode("utf-8")

    username = creds.split(":")[0]
    password = creds.split(":")[1] # Remove the last character as its a new line character

    logger.info(f"Username - {username}")

    response = validate_username(username)
    if response.status_code == 0:
        return JSONResponse(content=StatusResponse(status = 'User does not exists. Please check the username', datetime = str(datetime.now())).__dict__,
                            status_code = 400)
    
    resp = await get_user_details(username=username)

    resp_body_list = json.loads(resp.body.decode("utf-8"))

    for i in resp_body_list:
        hashed_password = (i["password"])

    if not settings.passwordhash.verify(password, hashed_password):
        return JSONResponse(content={"username" : username, "message" : "Invalid password"}, status_code=401)

    return JSONResponse(content={"username" : username, "message" : "Verification Successful"}, status_code=202)

@router.put("/updatepassword", response_model=Users, summary="Updates the user password")
async def update_password(request: Request) -> JSONResponse:
    update_credentials = await request.json()
    new_creds = base64.b64decode(update_credentials["new_credentials"]).decode("utf-8")

    resp = await validate_password(request=request)
    
    if resp.status_code != 202:
        return resp
    
    username = new_creds.split(":")[0]
    password = new_creds.split(":")[1][:-1]

    try:
        logger.info("Get Database Object")
        conn = settings.get_mariadb_cursor()
        cur = conn.cursor()

        query = f"UPDATE users SET password='{settings.passwordhash.hash(password)}' where username = '{username}'"

        logger.info(f"Query - {query}")

        cur.execute(query)
        conn.commit()

        ret_resp = StatusResponse(status = 'Success', datetime = str(datetime.now()))

        return JSONResponse(content=ret_resp.__dict__, status_code=201)
    
    except Exception as e:
        logger.exception(f"Exception occurred - {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()