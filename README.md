# Gorzdrav API Async Client

**Unofficial Async Python Client for Gorzdrav.spb.ru Appointment System**

---

## 📖 Overview

This library provides async Python bindings for interacting with Gorzdrav.spb.ru - St. Petersburg's medical appointment system. It enables programmatic access to:

- Medical institutions (LPUs)
- Specialty departments
- Doctor listings
- Available appointments
- Real-time schedule information

Built with `httpx` and `pydantic` for optimal asynchronous performance and type-safe data handling.

---

## ✨ Key Features

- 🚀 Async FastAPI server with UVicorn
- 🔄 Client connection pooling
- 🚶 Request queue management
- 🔐 Proper error handling
- 📚 Swagger documentation included

---

## 💻 Use Cases

- Automated appointment monitoring systems
- Medical resource availability dashboards
- Integration with healthcare notification services
- Urban medical service analysis tools

---

## 📦 Installation

TODO

## gorzdrav API Documentation

### Configuration
Edit `config.py` for:
- API connection parameters
- Server settings
- Pool size and queue limits

### Running the Server

TODO

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Example Requests

#### 1. Get All Districts
```bash
curl "http://localhost:8000/districts"
```

Example Response:
```json
[
  {
    "id": "5",
    "name": "Адмиралтейский"
  },
  {
    "id": "96",
    "name": "Василеостровский"
  }
]
```

#### 2. Get LPUs
```bash
curl "http://localhost:8000/lpus"
```

Or get LPUs in District
```bash
curl "http://localhost:8000/lpus?district_id=5"
```

Example Response:
```json
[
  {
    "id": 3,
    "address": "198261, Санкт-Петербург, ул. Генерала Симоняка, д. 6",
    "lpuFullName": "СПб ГБУЗ \"Городская поликлиника №88\""
  }
]
```

#### 3. Get Specialties in LPU
```bash
curl "http://localhost:8000/specialties?lpu_id=3"
```

Example Response:
```json
[
  {
    "id": "49351",
    "name": "Терапия",
    "countFreeParticipant": 504,
    "countFreeTicket": 504,
    "lastDate": "2026-01-16T19:30:00",
    "nearestDate": "2026-01-12T08:00:00"
  }
]
```

#### 4. Get Doctors by Specialty
```bash
curl "http://localhost:8000/doctors?lpu_id=3&specialty_id=92140679"
```

Example Response:
```json
[
  {
    "id": "2229",
    "name": "Абдурахимова Эсмира Гасановна",
    "freeParticipantCount": 30,
    "freeTicketCount": 30,
    "lastDate": "2026-01-16T15:18:00",
    "nearestDate": "2026-01-15T16:33:00",
    "ariaNumber": "10, 18, 19"
  }
]
```

#### 5. Get Doctor Appointments
```bash
curl "http://localhost:8000/appointments?lpu_id=3&doctor_id=2229"
```

Example Response:
```json
[
  {
    "id": "20735418",
    "visitStart": "2026-01-15T16:33:00",
    "visitEnd": "2026-01-15T16:44:00",
    "room": "218/ПО 88 к.2"
  }
]
```

#### 6. Parse Gorzdrav URL
```bash
curl "http://localhost:8000/parse-url?url=https://gorzdrav.spb.ru/service-free-schedule#..."
```

Example Response:
```json
{
  "valid": true,
  "result": {
    "districtId": "5",
    "lpuId": 42,
    "specialtyId": "8",
    "doctorId": "doctor-12345"
  }
}
```

### 7. Generate Appointment Link
```bash
curl "http://localhost:8000/generate-link?district_id=5&lpu_id=3&specialty_id=49351&doctor_id=2229"
```
```bash
{
  "url": "https://gorzdrav.spb.ru/service-free-schedule#%5B%7B%22district%22:%225%22%7D,%7B%22lpu%22:%223%22%7D,%7B%22speciality%22:%2249351%22%7D,%7B%22schedule%22:%222229%22%7D,%7B%22doctor%22:%222229%22%7D%5D"
}
```


### Python Client Example
```python
import httpx
from pprint import pprint

async def fetch_data():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Get 
        response = await client.get("/districts")
        districts = response.json()
        pprint(districts)
        
        # Get appointments for doctor
        params = {"lpu_id": 42, "doctor_id": "doctor-12345"}
        response = await client.get("/appointments", params=params)
        appointments = response.json()
        pprint(appointments)

# Run the async function
import asyncio
asyncio.run(fetch_data())
```

## Specific Errors

| Error code | Description |
|---|---|
| 645 | Не найдено расписание медицинского ресурса |
| 660 | Что-то пошло не так. Попробуйте записаться позже |
| 37 | Отсутствуют специальности для записи на приём. Для записи к врачу обратитесь в регистратуру или колл-центр медицинской организации |
| 602 | Медорганизация нам не ответила. Попробуйте записаться позже или обратитесь в регистратуру медорганизации |
