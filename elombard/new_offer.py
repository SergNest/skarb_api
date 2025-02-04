import httpx
import xml.etree.ElementTree as ET
from fastapi import APIRouter, HTTPException, Depends, Request
from httpx import TimeoutException

from auth import authenticate
from conf.config import settings
from typing import Optional, Dict, List

from elombard.schema import OfferSuccessResponse, OfferErrorResponse, OfferRequest, SOfferRequestXMl, \
    SOfferErrorResponseXMl
from utils.logger_config import logger

router = APIRouter(
    prefix='/offer',
    tags=['work with offers']
)


@router.post(
    "/new_offer",
    response_model=OfferSuccessResponse,
    responses={
        400: {"model": OfferErrorResponse, "description": "Bad Request"},
        500: {"model": OfferErrorResponse, "description": "Internal Server Error"}
    }
)
async def create_new_offer(request_data: List[OfferRequest], user: Optional[str] = Depends(authenticate)):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/new_offer/"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    # Логування прийнятих даних – перетворюємо кожен об'єкт на словник
    logger.bind(job="new_offer").info(
        "Received request for /new_offer with data: {data} by user: {user}",
        data=[offer.dict() for offer in request_data],
        user=user,
    )

    async with httpx.AsyncClient() as client:
        try:
            # Припускаємо, що зовнішнє API очікує масив об'єктів
            response = await client.post(
                central_base_api_url,
                json=[offer.dict() for offer in request_data],
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            logger.bind(job="new_offer").info(
                "External API responded successfully for /new_offer with data: {response_data}",
                response_data=response.json(),
            )

            return OfferSuccessResponse(status="success", data=response.json())

        except TimeoutException:
            logger.bind(job="new_offer").error(
                "Timeout error while connecting to external API for /new_offer. URL: {url}",
                url=central_base_api_url,
            )
            raise HTTPException(status_code=504, detail="External API timeout")

        except httpx.HTTPStatusError as e:
            logger.bind(job="new_offer").error(
                "External API error for /new_offer. Status: {status_code}, Error: {error}",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise HTTPException(status_code=e.response.status_code, detail="External API returned error")

        except httpx.RequestError as e:
            logger.bind(job="new_offer").error(
                "Request error while connecting to external API for /new_offer. Error: {error}",
                error=str(e),
            )
            raise HTTPException(status_code=500, detail="Error connecting to external API")


def parse_xml_to_dict(xml_data: str) -> Dict:
    """Функція для парсингу XML у Python-словник"""
    root = ET.fromstring(xml_data)
    data_dict = {child.tag: child.text for child in root}
    data_dict["TypeRequest"] = root.attrib.get("TypeRequest", "LidOffer")
    return data_dict


@router.post(
    "/new_offer_xml",
    response_model=OfferSuccessResponse,
    responses={
        400: {"model": SOfferErrorResponseXMl, "description": "Bad Request"},
        500: {"model": SOfferErrorResponseXMl, "description": "Internal Server Error"},
    },
)
async def receive_xml_and_send_json(
        request: Request,
        user: Optional[str] = Depends(authenticate),
):
    central_base_api_url = f"http://{settings.ip_central}:{settings.port_central}/central/hs/elombard/new_offer_main/"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    xml_body = await request.body()
    xml_str = xml_body.decode("utf-8")

    logger.bind(job="new_offer_xml").info(
        "Received XML request for /new_offer_xml: {data} by user: {user}",
        data=xml_str,
        user=user,
    )

    try:
        json_data = parse_xml_to_dict(xml_str)
        validated_data = SOfferRequestXMl(**json_data)  # Валідація через Pydantic

        logger.bind(job="new_offer_xml").info(
            "Converted XML to JSON: {json_data}",
            json_data=validated_data.dict(),
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(central_base_api_url, json=validated_data.dict(), headers=headers, timeout=30)
            response.raise_for_status()

            logger.bind(job="new_offer_xml").info(
                "External API responded successfully for /new_offer_xml with response: {response_data}",
                response_data=response.json(),
            )

            return OfferSuccessResponse(status="success", data=response.json())
    except TimeoutException:
        logger.bind(job="new_offer_xml").error(
            "Timeout error while connecting to external API for /new_offer_xml. URL: {url}",
            url=central_base_api_url,
        )
        raise HTTPException(status_code=504, detail="External API timeout")
    except ET.ParseError:
        logger.bind(job="new_offer_xml").error("Invalid XML received")
        raise HTTPException(status_code=400, detail="Invalid XML format")
    except httpx.HTTPStatusError as e:
        logger.bind(job="new_offer_xml").error(
            "External API error for /new_offer_xml. Status: {status_code}, Error: {error}",
            status_code=e.response.status_code,
            error=str(e),
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail="External API returned error",
        )
    except httpx.RequestError as e:
        logger.bind(job="new_offer_xml").error(
            "Request error while connecting to external API for /new_offer_xml. Error: {error}",
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail="Error connecting to external API",
        )
