import asyncio
import httpx
from datetime import datetime
from typing import Any, Optional
from pydantic import ValidationError

from .models import (
    ApiResponse,
    ApiDistrict,
    ApiLPU,
    ApiSpecialty,
    ApiDoctor,
    ApiAppointment,
    ApiTimetable,
    Doctor,
    LinkParsingResult
)
from . import exceptions
from config import Config

class AsyncGorzdrav:
    """
    Async API client for Gorzdrav.spb.ru using httpx
    """
    def __init__(self, headers: Optional[dict] = None):
        self.api_url = Config.API_URL
        self.shared_url = f"{self.api_url}/shared"
        self.schedule_url = f"{self.api_url}/schedule"
        self.headers = headers or Config.HEADERS
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            http2=True
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    @staticmethod
    def generate_link(
        districtId: str,
        lpuId: int,
        specialtyId: str,
        scheduleId: str,
    ) -> str:
        """URL generator (remains unchanged)"""
        base_link = "https://gorzdrav.spb.ru/service-free-schedule#"
        addon = f"""%5B%7B%22district%22:%22{districtId}%22%7D,%7B%22lpu%22:%22{lpuId}%22%7D,%7B%22speciality%22:%22{specialtyId}%22%7D,%7B%22schedule%22:%22{scheduleId}%22%7D,%7B%22doctor%22:%22{scheduleId}%22%7D%5D"""
        return base_link + addon

    async def __get_result(
        self,
        url: str,
        sleep_time: float = 1.0,
        attempts: int = 3
    ) -> Any:
        """
        Async request handler with retry logic
        """
        for attempt in range(attempts):
            try:
                if sleep_time > 0.05:
                    await asyncio.sleep(sleep_time)
                
                response = await self.client.get(url)
                response.raise_for_status()
                response_json = response.json()
                
                api_response = ApiResponse(**response_json)
                if not api_response.success:
                    raise exceptions.GorzdravException(
                        message=api_response.message,
                        errorCode=api_response.errorCode,
                        url=url
                    )
                return api_response.result
            
            except httpx.HTTPStatusError as e:
                if attempt == attempts - 1:
                    raise exceptions.GorzdravExceptionBase(
                        message=f"HTTP error {e.response.status_code}",
                        url=url
                    ) from e
                await asyncio.sleep(2 ** attempt)
                
            except httpx.RequestError as e:
                if attempt == attempts - 1:
                    raise exceptions.GorzdravExceptionBase(
                        message=f"Network error: {str(e)}",
                        url=url
                    ) from e
                await asyncio.sleep(2 ** attempt)
                
            except ValidationError as e:
                raise exceptions.GorzdravExceptionBase(
                    message=f"Response validation error: {str(e)}",
                    url=url
                ) from e

    def __parse_list_in_result(self, objects: list[Any], model: Any) -> list[Any]:
        """Parse list of results into Pydantic models"""
        return [model(**result) for result in objects]
    
    async def get_districts(self) -> list[ApiDistrict]:
        """Get all districts"""
        url = f"{self.shared_url}/districts"
        result = await self.__get_result(url)
        return self.__parse_list_in_result(result, ApiDistrict)

    async def get_lpus(self, districtId: Optional[str] = None) -> list[ApiLPU]:
        """Get medical institutions (LPUs)"""
        if districtId:
            url = f"{self.shared_url}/district/{districtId}/lpus"
        else:
            url = f"{self.shared_url}/lpus"
        
        result = await self.__get_result(url)
        return self.__parse_list_in_result(result, ApiLPU)

    async def get_lpu(self, lpuId: int) -> ApiLPU:
        """Get specific medical institution"""
        url = f"{self.shared_url}/lpu/{lpuId}"
        result = await self.__get_result(url)
        return ApiLPU(**result)

    async def get_specialties(self, lpuId: int) -> list[ApiSpecialty]:
        """Get specialties for an institution"""
        url = f"{self.schedule_url}/lpu/{lpuId}/specialties"
        try:
            result = await self.__get_result(url)
            return self.__parse_list_in_result(result, ApiSpecialty)
        except exceptions.NoSpecialtiesException:
            return []

    async def get_doctors(self, lpuId: int, specialtyId: str) -> list[ApiDoctor]:
        """Get doctors by specialty"""
        url = f"{self.schedule_url}/lpu/{lpuId}/speciality/{specialtyId}/doctors"
        try:
            result = await self.__get_result(url)
            return self.__parse_list_in_result(result, ApiDoctor)
        except exceptions.NoDoctorsException:
            return []

    async def get_doctor(
        self,
        lpuId: int,
        specialtyId: str,
        doctorId: str,
        districtId: Optional[str] = None
    ) -> Optional[Doctor]:
        """Get specific doctor"""
        doctors = await self.get_doctors(lpuId, specialtyId)
        for doctor in doctors:
            if doctor.id == doctorId:
                return Doctor(
                    **doctor.model_dump(),
                    districtId=districtId,
                    lpuId=lpuId,
                    specialtyId=specialtyId
                )
        return None

    async def get_timetables(self, lpu_id: int, doctor_id: str) -> list[ApiTimetable]:
        """Get doctor's timetable"""
        url = f"{self.schedule_url}/lpu/{lpu_id}/doctor/{doctor_id}/timetable"
        result = await self.__get_result(url)
        return self.__parse_list_in_result(result, ApiTimetable)

    async def get_appointments(self, lpu_id: int, doctor_id: str) -> list[ApiAppointment]:
        """Get available appointments"""
        url = f"{self.schedule_url}/lpu/{lpu_id}/doctor/{doctor_id}/appointments"
        try:
            result = await self.__get_result(url)
            return self.__parse_list_in_result(result, ApiAppointment)
        except exceptions.NoTicketsException:
            return []