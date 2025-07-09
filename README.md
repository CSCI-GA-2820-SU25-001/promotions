[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU25-001/promotions/graph/badge.svg?token=A2FO1SPNW5)](https://codecov.io/gh/CSCI-GA-2820-SU25-001/promotions)
# Promotions REST API
This is a RESTful microservice for managing promotions as part of an eCommerce backend. It allows you to create, read, update, delete, and list product promotions such as percentage discounts, amount off, and BOGO (Buy One Get One) offers.
---
## :rocket: Features
- Create a new promotion
- Retrieve a promotion by ID
- List all promotions
- Update an existing promotion
- Delete a promotion
- JSON-only input/output
- Logging and TDD-based testing
- Error-handling for unsupported methods and content types
---
## :bricks: Tech Stack
- Python 3.11
- Flask
- PostgreSQL (via SQLAlchemy)
- Docker + Docker Compose
- PyUnit (unittest)
- Coverage
- Pylint (PEP8 conformance)
- ZenHub + GitHub Projects
---
## :package: Installation & Setup
Clone the repository:
```bash
git clone https://github.com/nyu-devops-squad/promotions.git
cd promotions
```
Start the development environment:
```bash
make setup
```
Start the service with Docker:
```bash
honcho start
```
Open your browser and visit:
http://localhost:8080/
---
## :test_tube: Running Tests
Run all tests and check coverage:
```bash
make test
```
Run lint checks (PEP8 compliance):
```bash
make lint
```
---
## :books: API Endpoints
All requests and responses are in application/json format.
| Method | Endpoint         | Description            |
|--------|---------------------------|-----------------------------------|
| GET  | /             | Returns service metadata     |
| POST  | /promotions        | Creates a new promotion      |
| GET  | /promotions        | Lists all promotions       |
| GET  | /promotions/{id}     | Gets promotion by ID       |
| PUT  | /promotions/{id}     | Updates promotion by ID      |
| DELETE | /promotions/{id}     | Deletes promotion by ID      |
---
## :outbox_tray: Sample API Calls
Create a Promotion:
```bash
http POST :8080/promotions name=“Flash Sale” promo_type=“PERCENT_OFF” product_id=101 amount=15.0 start_date=“2025-07-01” end_date=“2025-07-31"
```
List All Promotions:
```bash
http GET :8080/promotions
```
Read a Promotion:
```bash
http GET :8080/promotions/1
```
Update a Promotion:
```bash
http PUT :8080/promotions/1 name=“Updated” promo_type=“AMOUNT_OFF” product_id=101 amount=5.0 start_date=“2025-07-01” end_date=“2025-07-31"
```
Delete a Promotion:
```bash
http DELETE :8080/promotions/1
```
---
## :octagonal_sign: Error Handling
- 404 Not Found – if promotion ID doesn’t exist
- 400 Bad Request – mismatched ID in URL and body
- 415 Unsupported Media Type – if Content-Type is not application/json
- All errors return JSON responses only
---
## :chart_with_upwards_trend: Code Coverage
- All model and route code is tested with PyUnit
- 95%+ test coverage achieved via test_models.py and test_routes.py