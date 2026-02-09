# Credit Approval System

A production-ready Django REST API backend for credit approval and loan management system.

## Features

- Customer registration with automatic credit limit calculation
- Credit score calculation based on historical loan data
- Loan eligibility checking with dynamic interest rate adjustment
- Loan creation with EMI calculation using compound interest
- Background workers for Excel data ingestion
- PostgreSQL database with proper indexing
- Dockerized deployment with docker-compose

## Tech Stack

- Django 4.2.9
- Django REST Framework
- PostgreSQL 15
- Celery + Redis (Background Tasks)
- Docker & Docker Compose
- openpyxl (Excel file processing)

## Project Structure

credit-approval-system/
├── apps/
│   ├── customers/      # Customer management
│   ├── loans/          # Loan management
│   └── core/           # Shared services (credit score, EMI calculator)
├── config/             # Django configuration
├── data/               # Excel files for data ingestion
└── docker-compose.yml  # Docker orchestration

## Setup Instructions

### Prerequisites

- Docker & Docker Compose installed
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd credit-approval-system
```

2. Create environment file:
```bash
cp .env.example .env
```
Edit `.env` file with your configurations (default values work for development).

3. Add Excel files:
Place `customer_data.xlsx` and `loan_data.xlsx` in the parent folder (same level as `credit-approval-system/`).

4. Build and start services:
```bash
docker-compose up --build
```

5. Run migrations (in a new terminal):
```bash
docker-compose exec web python manage.py migrate
```

6. Create superuser (optional):
```bash
docker-compose exec web python manage.py createsuperuser
```

7. Trigger data ingestion:
```bash
docker-compose exec web python manage.py shell
```
In the shell:
```python
from apps.core.tasks import ingest_all_data
ingest_all_data.delay()
exit()
```

The application will be available at `http://localhost:8000`.

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

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.
