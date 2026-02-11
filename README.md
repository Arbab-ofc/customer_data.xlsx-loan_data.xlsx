# Credit Approval System

![Django](https://img.shields.io/badge/Django-4.2.9-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.14.0-ff1709?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3.4-37814A?logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-5.0.1-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

A production-ready Django REST API for credit approval and loan management. The service calculates credit limits and credit scores, checks eligibility with dynamic interest rate correction, and creates loans with EMI calculations. Excel-based ingestion is supported for bulk data bootstrapping.

## Features

- Customer registration with automatic approved limit calculation
- Credit score computation based on payment history and loan portfolio
- Eligibility checks with interest rate correction and EMI affordability guardrails
- Loan creation with EMI computed via compound interest
- Background ingestion from Excel using Celery
- PostgreSQL-backed persistence with Docker support

## Tech Stack

- Django + Django REST Framework
- PostgreSQL
- Celery + Redis
- openpyxl
- Docker + Docker Compose

## Project Structure

credit-approval-system/
├── apps/
│   ├── customers/      # Customer management
│   ├── loans/          # Loan management
│   └── core/           # Shared services (credit score, EMI calculator)
├── config/             # Django configuration
├── data/               # Excel files for data ingestion
└── docker-compose.yml  # Docker orchestration

## Data Files (Required)

The application expects Excel files in `data/`.

## Clone Repository

```bash
git clone <repository-url>
cd credit-approval-system
```

Option A: clone the data repo into `data/`:
```bash
git clone https://github.com/Arbab-ofc/customer_data.xlsx-loan_data.xlsx data
```

Option B: download the files and place them in `data/`:
- `customer_data.xlsx`
- `loan_data.xlsx`

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 6+
- Docker (optional)
- Git

### Local Development (No Docker)

1. Clone the repository:
```bash
git clone <repository-url>
cd credit-approval-system
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (example):
```bash
export DB_NAME=credit_approval_db
export DB_USER=<your_db_user>
export DB_PASSWORD=<your_db_password>
export DB_HOST=localhost
export DB_PORT=5432
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the dev server:
```bash
python manage.py runserver
```

7. Trigger data ingestion (optional):
```bash
python manage.py shell
```
In the shell:
```python
from apps.core.tasks import ingest_all_data
ingest_all_data.delay()
exit()
```

The application will be available at `http://localhost:8000`.

### Docker (Optional)

```bash
docker-compose up --build
```
In another terminal:
```bash
docker-compose exec web python manage.py migrate
```

## API Endpoints

### 1. Register Customer
POST `/register`

Request:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": 9876543210
}
```

Response:
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": 9876543210
}
```

### 2. Check Eligibility
POST `/check-eligibility`

Request:
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.5,
  "tenure": 24
}
```

Response:
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.5,
  "corrected_interest_rate": 12.0,
  "tenure": 24,
  "monthly_installment": 9415.67
}
```

### 3. Create Loan
POST `/create-loan`

Request:
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.5,
  "tenure": 24
}
```

Response:
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 9415.67
}
```

### 4. View Loan Details
GET `/view-loan/<loan_id>`

Response:
```json
{
  "loan_id": 1,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": 9876543210,
    "age": 30
  },
  "loan_amount": 200000,
  "interest_rate": 12.0,
  "monthly_installment": 9415.67,
  "tenure": 24
}
```

### 5. View Customer Loans
GET `/view-loans/<customer_id>`

Response:
```json
[
  {
    "loan_id": 1,
    "loan_amount": 200000,
    "interest_rate": 12.0,
    "monthly_installment": 9415.67,
    "repayments_left": 24
  }
]
```

## cURL Examples

Register Customer:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": 9876543210
  }'
```

Check Eligibility:
```bash
curl -X POST http://localhost:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 200000,
    "interest_rate": 10.5,
    "tenure": 24
  }'
```

Create Loan:
```bash
curl -X POST http://localhost:8000/create-loan \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 200000,
    "interest_rate": 12.0,
    "tenure": 24
  }'
```

View Loan:
```bash
curl http://localhost:8000/view-loan/1
```

View Customer Loans:
```bash
curl http://localhost:8000/view-loans/1
```

## Local Endpoint Test Results (No Docker)

Tested locally against a running dev server using a fresh Postgres database.

### 1. Register Customer
Endpoint: `POST /register`

Request:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": 9876543210
}
```

Result:
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": "50000.00",
  "approved_limit": "1800000.00",
  "phone_number": 9876543210
}
```

### 2. Check Eligibility
Endpoint: `POST /check-eligibility`

Request:
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.5,
  "tenure": 24
}
```

Result:
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.5,
  "corrected_interest_rate": 12.0,
  "tenure": 24,
  "monthly_installment": 9414.69
}
```

### 3. Create Loan
Endpoint: `POST /create-loan`

Request:
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.5,
  "tenure": 24
}
```

Result:
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 9414.69
}
```

### 4. View Loan Details
Endpoint: `GET /view-loan/1`

Result:
```json
{
  "loan_id": 1,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": 9876543210,
    "age": 30
  },
  "loan_amount": "200000.00",
  "interest_rate": "12.00",
  "monthly_installment": "9414.69",
  "tenure": 24
}
```

### 5. View Customer Loans
Endpoint: `GET /view-loans/1`

Result:
```json
[
  {
    "loan_id": 1,
    "loan_amount": "200000.00",
    "interest_rate": "12.00",
    "monthly_installment": "9414.69",
    "repayments_left": 24
  }
]
```

## Business Logic

### Credit Limit Calculation
`approved_limit = 36 * monthly_salary` rounded to nearest lakh (100,000).

### Credit Score Calculation (0-100)
Factors:

1. Payment History (40 points): Percentage of EMIs paid on time
2. Number of Loans (20 points): Optimal is 2-5 loans
3. Current Year Activity (20 points): Active loans in current year
4. Loan Volume (20 points): Total approved loan amount
5. Critical Factor: If current loans > approved_limit -> score = 0

### Loan Approval Rules

- Credit Score > 50: Approve at requested rate
- 30 < Score <= 50: Approve if rate > 12%, else correct to 12%
- 10 < Score <= 30: Approve if rate > 16%, else correct to 16%
- Score <= 10: Reject
- EMI Check: Reject if sum of current EMIs > 50% of monthly salary

### EMI Calculation
Uses compound interest formula:
`EMI = P * r * (1+r)^n / ((1+r)^n - 1)`

Where:
- P = Principal loan amount
- r = Monthly interest rate (annual_rate / 12 / 100)
- n = Tenure in months

## Development

Run tests:
```bash
docker-compose exec web python manage.py test
```

Access Django shell:
```bash
docker-compose exec web python manage.py shell
```

View logs:
```bash
docker-compose logs -f web
docker-compose logs -f celery_worker
```

Stop services:
```bash
docker-compose down
```

Stop and remove volumes:
```bash
docker-compose down -v
```

## Monitoring Celery Tasks

Check Celery worker logs:
```bash
docker-compose logs -f celery_worker
```

Monitor tasks using Django admin or Celery Flower (can be added separately).

## Database Access

Connect to PostgreSQL:
```bash
docker-compose exec db psql -U postgres -d credit_approval_db
```

## Production Considerations

1. Change SECRET_KEY in .env
2. Set DEBUG=False
3. Configure proper ALLOWED_HOSTS
4. Use production-grade WSGI server (gunicorn included)
5. Set up SSL/TLS certificates
6. Configure proper logging
7. Set up monitoring (Sentry, New Relic, etc.)
8. Use Redis Sentinel or Redis Cluster for high availability
9. Set up database backups
10. Configure rate limiting

## Excel File Format

customer_data.xlsx columns:
`customer_id, first_name, last_name, phone_number, monthly_salary, approved_limit, current_debt`

loan_data.xlsx columns:
`customer_id, loan_id, loan_amount, tenure, interest_rate, monthly_repayment, EMIs paid on time, start_date, end_date`

## Contact

![GitHub](https://img.shields.io/badge/GitHub-Arbab--ofc-181717?logo=github&logoColor=white)
![Email](https://img.shields.io/badge/Email-arbabprvt%40gmail.com-D14836?logo=gmail&logoColor=white)

- GitHub: https://github.com/Arbab-ofc
- Email: mailto:arbabprvt@gmail.com
- Issues: Please open an issue in this repository.
