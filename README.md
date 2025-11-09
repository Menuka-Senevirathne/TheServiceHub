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
- Git  
- (Optional) A running instance of WSO2 API Manager if you plan to publish the API

### Installation

```bash
# Clone the repository
git clone https://github.com/Menuka-Senevirathne/TheServiceHub.git
cd TheServiceHub

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
