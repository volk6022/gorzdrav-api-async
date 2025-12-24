# Technical documentation - how it works

**Base URL:** `https://gorzdrav.spb.ru/_api/api/v2`

## Data Models

This section details the Pydantic models used for data validation and structuring.

### ApiResponse

The base model for all API responses.

| Field | Type | Description |
|---|---|---|
| `result` | `Any | None` | The actual data returned by the API. |
| `success` | `bool` | Indicates if the request was successful. |
| `errorCode` | `int` | The error code, if any. |
| `message` | `str | None` | A descriptive message about the response. |
| `stackTrace` | `Any | None` | The stack trace in case of an error. |
| `requestId` | `str | None` | A unique identifier for the request. |

### ApiDistrict

Represents a district.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The unique identifier of the district. |
| `name` | `str` | The name of the district. |

### ApiLPU

Represents a medical institution (LPU).

| Field | Type | Description |
|---|---|---|
| `id` | `int` | The unique identifier of the LPU. |
| `address` | `str | None` | The address of the LPU. |
| `lpuFullName`| `str | None` | The full name of the LPU. |

### ApiSpecialty

Represents a medical specialty.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The unique identifier of the specialty. |
| `name` | `str | None` | The name of the specialty. |
| `countFreeParticipant`| `int | None` | The number of free slots for this specialty. |
| `countFreeTicket`| `int | None` | The number of free tickets for this specialty. |
| `lastDate` | `datetime | None`| The date of the last available appointment. |
| `nearestDate` | `datetime | None`| The date of the nearest available appointment. |

### ApiDoctor

Represents a doctor.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The unique identifier of the doctor. |
| `name` | `str` | The name of the doctor. |
| `freeParticipantCount`| `int` | The number of free slots for this doctor. |
| `freeTicketCount`| `int` | The number of free tickets for this doctor. |
| `lastDate` | `datetime | None`| The date of the last available appointment. |
| `nearestDate` | `datetime | None`| The date of the nearest available appointment. |
| `ariaNumber` | `str | None` | The area number. |

### ApiAppointment

Represents an appointment slot.

| Field | Type | Description |
|---|---|---|
| `id` | `str` | The unique identifier of the appointment. |
| `visitStart` | `datetime | None`| The start time of the appointment. |
| `visitEnd` | `datetime | None` | The end time of the appointment. |
| `room` | `str | None` | The room number for the appointment. |

### ApiTimetable

Represents a doctor's timetable for a specific day.

| Field | Type | Description |
|---|---|---|
| `appointments`| `list[ApiAppointment]` | A list of appointments for the day. |
| `denyCause` | `str | None` | The reason if the day is not available for booking. |
| `recordableDay`| `bool` | Indicates if it's possible to book an appointment on this day. |
| `visitStart` | `datetime | None`| The start time of the first appointment of the day. |
| `visitEnd` | `datetime | None` | The end time of the last appointment of the day. |

### Doctor

Extends `ApiDoctor` with additional information.

| Field | Type | Description |
|---|---|---|
| `districtId`| `str | None` | The ID of the district. |
| `lpuId` | `int` | The ID of the medical institution. |
| `specialtyId`| `str` | The ID of the specialty. |

### LinkParsingResult

Represents the result of parsing a Gorzdrav URL.

| Field | Type | Description |
|---|---|---|
| `districtId`| `str` | The ID of the district. |
| `lpuId` | `int` | The ID of the medical institution. |
| `specialtyId`| `str` | The ID of the specialty. |
| `doctorId` | `str | None` | The ID of the doctor. |

## Gorzdrav Class

This class provides methods to interact with the Gorzdrav API.

### `generate_link(districtId: str, lpuId: int, specialtyId: str, scheduleId: str) -> str`

Generates a URL to the appointment booking page on gorzdrav.spb.ru.

*   **Parameters:**
    *   `districtId` (str): The ID of the district.
    *   `lpuId` (int): The ID of the medical institution.
    *   `specialtyId` (str): The ID of the specialty.
    *   `scheduleId` (str): The ID of the schedule (can be the doctor's ID).
*   **Returns:** A URL string.

### `get_districts() -> list[ApiDistrict]`

Retrieves a list of all districts.

*   **Endpoint:** `GET /shared/districts`
*   **Returns:** A list of `ApiDistrict` objects.
*   **Exceptions:**
    *   `GorzdravExceptionBase`: For general API errors.
    *   `requests.exceptions.RequestException`: For network-related errors.

### `get_lpus(districtId: str | None = None) -> list[ApiLPU]`

Retrieves a list of medical institutions (LPUs).

*   **Endpoint:**
    *   `GET /shared/lpus` (if `districtId` is not provided)
    *   `GET /shared/district/{districtId}/lpus` (if `districtId` is provided)
*   **Parameters:**
    *   `districtId` (str, optional): The ID of the district to filter by.
*   **Returns:** A list of `ApiLPU` objects.
*   **Exceptions:**
    *   `GorzdravExceptionBase`: For general API errors.
    *   `requests.exceptions.RequestException`: For network-related errors.

### `get_lpu(lpuId: int) -> ApiLPU`

Retrieves information about a specific medical institution.

*   **Endpoint:** `GET /shared/lpu/{lpuId}`
*   **Parameters:**
    *   `lpuId` (int): The ID of the LPU.
*   **Returns:** An `ApiLPU` object.
*   **Exceptions:**
    *   `GorzdravExceptionBase`: For general API errors.
    *   `requests.exceptions.RequestException`: For network-related errors.

### `get_specialties(lpuId: int) -> list[ApiSpecialty]`

Retrieves a list of specialties for a given medical institution.

*   **Endpoint:** `GET /schedule/lpu/{lpuId}/specialties`
*   **Parameters:**
    *   `lpuId` (int): The ID of the LPU.
*   **Returns:** A list of `ApiSpecialty` objects.
*   **Exceptions:**
    *   `NoSpecialtiesException`: If no specialties are found for the LPU.
    *   `GorzdravExceptionBase`: For other general API errors.
    *   `requests.exceptions.RequestException`: For network-related errors.

### `get_doctors(lpuId: int, specialtyId: str) -> list[ApiDoctor]`

Retrieves a list of doctors for a given medical institution and specialty.

*   **Endpoint:** `GET /schedule/lpu/{lpuId}/speciality/{specialtyId}/doctors`
*   **Parameters:**
    *   `lpuId` (int): The ID of the LPU.
    *   `specialtyId` (str): The ID of the specialty.
*   **Returns:** A list of `ApiDoctor` objects.
*   **Exceptions:**
    *   `NoDoctorsException`: If no doctors are found for the given specialty.
    *   `GorzdravExceptionBase`: For other general API errors.
    *   `requests.exceptions.RequestException`: For network-related errors.

### `get_doctor(lpuId: int, specialtyId: str, doctorId: str, districtId: str | None = None) -> Doctor | None`

Retrieves information about a specific doctor.

*   **Calls:** `get_doctors()`
*   **Parameters:**
    *   `lpuId` (int): The ID of the LPU.
    *   `specialtyId` (str): The ID of the specialty.
    *   `doctorId` (str): The ID of the doctor.
    *   `districtId` (str, optional): The ID of the district.
*   **Returns:** A `Doctor` object if found, otherwise `None`.
*   **Exceptions:** See `get_doctors()`.

### `get_timetables(lpu_id: int, doctor_id: str) -> list[ApiTimetable]`

Retrieves the timetable for a specific doctor.

*   **Endpoint:** `GET /schedule/lpu/{lpu_id}/doctor/{doctor_id}/timetable`
*   **Parameters:**
    *   `lpu_id` (int): The ID of the LPU.
    *   `doctor_id` (str): The ID of the doctor.
*   **Returns:** A list of `ApiTimetable` objects.
*   **Exceptions:**
    *   `GorzdravExceptionBase`: For general API errors.
    *   `requests.exceptions.RequestException`: For network-related errors.

### `get_appointments(lpu_id: int, doctor_id: str) -> list[ApiAppointment]`

Retrieves the available appointment slots for a specific doctor.

*   **Endpoint:** `GET /schedule/lpu/{lpu_id}/doctor/{doctor_id}/appointments`
*   **Parameters:**
    *   `lpu_id` (int): The ID of the LPU.
    *   `doctor_id` (str): The ID of the doctor.
*   **Returns:** A list of `ApiAppointment` objects.
*   **Exceptions:**
    *   `NoTicketsException`: If there are no available appointments.
    *   `GorzdravExceptionBase`: For other general API errors.
    *   `requests.exceptions.RequestException`: For network-related errors.

## Exceptions

The client uses a set of custom exceptions to handle API errors.

### `GorzdravExceptionBase(Exception)`

The base exception for all Gorzdrav API client errors.

*   **Attributes:**
    *   `message` (str | None): The error message from the API.
    *   `errorCode` (int | None): The error code from the API.
    *   `url` (str | None): The URL that caused the error.

### `NoDoctorsException(GorzdravExceptionBase)`

Raised when there are no available doctors for the requested specialty.

*   **`default_message`**: "Отсутствуют специалисты для приёма по выбранной специальности. Обратитесь в регистратуру медорганизации"
*   **`default_errorCode`**: 38

### `NoTicketsException(GorzdravExceptionBase)`

Raised when there are no available tickets for a doctor.

*   **`default_message`**: "Отсутствуют свободные талоны. Попробуйте записаться позже или обратитесь в регистратуру медорганизации"
*   **`default_errorCode`**: 39

### `NoSpecialtiesException(GorzdravExceptionBase)`

Raised when there are no specialties available for booking.

*   **`default_message`**: "Отсутствуют специальности для записи на приём. Для записи к врачу обратитесь в регистратуру или колл-центр медицинской организации"
*   **`default_errorCode`**: 39

### `Api616Exception(GorzdravExceptionBase)`

Raised for a specific medical information system error.

*   **`default_message`**: "Возникла ошибка в работе медицинской информационной системы медицинской организации. Попробуйте позже или обратитесь в регистратуру медицинской организации."
*   **`default_errorCode`**: 616

### `Api603Exception(GorzdravExceptionBase)`

Raised when the request to the medical organization's system times out.

*   **`default_message`**: "Время ожидания ответа от медицинской организации истекло. Попробуйте записаться позже или обратитесь в регистратуру медицинской организации."
*   **`default_errorCode`**: 603

### `GorzdravException(GorzdravExceptionBase)`

A factory-like class that raises a more specific exception based on the `errorCode`.

*   **Logic:**
    *   `errorCode` 37: raises `NoSpecialtiesException`
    *   `errorCode` 38: raises `NoDoctorsException`
    *   `errorCode` 39: raises `NoTicketsException`
    *   `errorCode` 616: raises `Api616Exception`
    *   `errorCode` 603: raises `Api603Exception`
    *   Other codes: raises `GorzdravExceptionBase`

## URL Validation and Parsing

The `validate.py` module provides functions to validate and parse gorzdrav.spb.ru URLs.

### `is_gorzdrav(url: str) -> bool`

Checks if a URL belongs to the gorzdrav.spb.ru free schedule service.

*   **Returns:** `True` if the URL matches, `False` otherwise.

### `get_ids_from_gorzdrav_url(url: str) -> LinkParsingResult | None`

Parses a Gorzdrav URL to extract district, LPU, specialty, and doctor IDs using regular expressions.

*   **Returns:** A `LinkParsingResult` object on successful parsing, otherwise `None`.

### `parse_url(url: str) -> LinkParsingResult | None`

Parses a Gorzdrav URL by decoding it and loading the relevant part as JSON to extract district, LPU, specialty, and doctor IDs.

*   **Returns:** A `LinkParsingResult` object on successful parsing, otherwise `None`.