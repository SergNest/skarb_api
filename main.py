import uvicorn
import httpx

from fastapi import FastAPI, HTTPException, status, Header
from fastapi.security import HTTPBearer

from conf.config import settings

app = FastAPI()
security = HTTPBearer()

expected_token = settings.expected_token


@app.get("/api/healthchecker")
def healthchecker():
    try:

        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")


@app.get("/")
async def root():
    return {"message": "Hello Skarb"}


@app.get("/dogovorhistory/{client_id}")
async def get_data_from_external_api(client_id: str, authorization: str = Header(None)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/history/dogovorhistory/{client_id}"
    if authorization != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url, timeout=500.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error connecting to external API")


@app.get("/gettype/{search}")
async def get_data_from_external_api(search: str, authorization: str = Header(None)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/model/gettype/{search}"
    if authorization != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(central_base_api_url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error connecting to external API")


if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True, port=55335)
