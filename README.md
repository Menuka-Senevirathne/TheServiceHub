# TheServiceHub

A RESTful backend service for managing vehicle service appointments and invoice uploads.  
Built with Flask, SQLAlchemy (SQLite), and designed to be exposed via an API gateway (e.g., WSO2 API Manager).

---

## Table of Contents

- [Features](#features)  
- [Architecture](#architecture)  
- [Getting Started](#getting-started)  
- [Usage](#usage)  
- [API Endpoints](#api-endpoints)  
- [Database Models](#database-models)  
- [Contributing](#contributing)  
- [License](#license)

---

## Features

- Create, list, and update **appointments** (vehicle service jobs).  
- Upload, retrieve, and manage **invoices** (PDFs).  
- Auto‑generated unique integer IDs for both appointments and invoices (clients do *not* send IDs).  
- Status lifecycle for invoices (“draft” → “approved” / “rejected”).  
- Ready for API gateway fronting (JWT authentication, routing via WSO2 APIM, etc.).  
- Seed script to populate sample data for quick local testing.

---

## Architecture

- **Flask**: REST API server  
- **SQLAlchemy + SQLite**: Data persistence (lightweight for demo / small‑scale)  
- **Uploads Folder**: Stores uploaded PDF invoice files  
- **Seed Data**: A `seed.py` script to initialize the database and sample records

---

## Getting Started

### Prerequisites

- Python 3.x  
- `pipenv` or `virtualenv` (recommended)  


### Installation

```bash
# Clone the repository
git clone https://github.com/Menuka-Senevirathne/TheServiceHub.git
cd TheServiceHub

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt

# Insert sample data
python3 python3 seed.py

# Starting the app
python3 app.py

```

## API Endpoints

Here’s a summary of the endpoints (base URL `http://127.0.0.1:5001`):

### Appointments

| Method | Path                  | Description                     |
|--------|----------------------|---------------------------------|
| POST   | `/appointments`       | Create new appointment          |
| GET    | `/appointments`       | List all appointments           |
| GET    | `/appointments/{id}`  | Retrieve specific appointment   |
| PATCH  | `/appointments/{id}`  | Update status of appointment (`scheduled`, `rejected`)   |

### Invoices

| Method | Path                | Description                            |
|--------|--------------------|----------------------------------------|
| POST   | `/invoices`        | Upload a PDF invoice (multipart)       |
| GET    | `/invoices`        | List all invoices                       |
| GET    | `/invoices/{id}`   | Retrieve specific invoice               |
| PATCH  | `/invoices/{id}`   | Update status (`approved`, `rejected`)     |


## Sample API Usage

### 1. Making an Appointment

**Request:**

```
curl --location 'http://127.0.0.1:5001/appointments' \
--header 'Content-Type: application/json' \
--data '{
    "customer_id": 5,
    "vehicle_category": "SUV",
    "job_description": "Body wash"
}'
```
**Response:**

```
{
    "appointment": {
        "id": 6,
        "links": {
            "self": "http://127.0.0.1:5001/appointments/6"
        },
        "status": "pending"
    },
    "message": "Appointment created successfully"
}
```
### 2. Confirming an Appointment (PATCH)

**Request:**
```
curl --location --request PATCH 'http://127.0.0.1:5001/appointments/6' \
--header 'Content-Type: application/json' \
--data '{"status": "scheduled"}'
```
**Response:**
```
{
    "message": "Status updated successfully",
    "status": "scheduled"
}
```

### 3. Drafting an Invoice with a PDF File

**Request:**
```
curl --location 'http://127.0.0.1:5001/invoices' \
--header 'accept: application/json' \
--form 'branch_manager="Fred"' \
--form 'branch="Gampaha"' \
--form 'total_cost="22000"' \
--form 'upload_file=@"/Users/menukasenevirathne/Documents/SupportTickets/TheProject/PDF/invoice.pdf"'
```
**Response:**
```
{
    "invoice": {
        "filename": "invoice.pdf",
        "id": 10,
        "links": {
            "self": "http://127.0.0.1:5001/invoices/10"
        },
        "status": "drafted"
    },
    "message": "Invoice uploaded successfully"
}
```

### 4. Approving an Invoice (PATCH)

**Request:**
```
curl --location --request PATCH 'http://127.0.0.1:5001/invoices/10' \
--header 'Content-Type: application/json' \
--data '{
    "status": "approved"
}'
```
**Response:**

```
{
    "invoice_id": 10,
    "message": "Invoice status updated to approved",
    "status": "approved"
}
```


