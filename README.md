Digital Wallet System Backend

Overview

This is a Flask-based RESTful API backend for a Digital Wallet system. It supports user registration, JWT-based authentication, wallet balance management (deposit, withdraw, transfer), transaction tracking, and basic fraud detection (flags transactions exceeding a configurable threshold). Admin users can view flagged transactions.

Features

* User registration and login with JWT authentication
* Multi-currency wallet balance management
* Deposit, withdrawal, and transfer of funds
* Transaction logging with unique IDs and timestamps
* Fraud detection for large transactions
* Soft deletion of users and transactions
* Admin APIs for flagged transaction review


Setup Instructions

1. Clone the repository

bash
git clone <your-repo-url>
cd <your-repo-folder>


2. Create and activate a Python virtual environment

bash
python3 -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows


3. Install dependencies

bash
pip install -r requirements.txt


4. Set environment variables

Create a .env file or export environment variables directly. At minimum, define:

bash
FLASK_APP=app.py
FLASK_ENV=development
JWT_SECRET_KEY=your_jwt_secret_key_here


5. Run the Flask app

bash
flask run


The API will be available at http://localhost:5000.


API Endpoints

Authentication

* POST /register — Register a new user
* POST /login — Login and receive JWT token

Wallet Operations (JWT required)

* GET /balance?currency=USD — Get wallet balance for user
* POST /deposit — Deposit funds into wallet
* POST /withdraw — Withdraw funds from wallet
* POST /transfer — Transfer funds to another user
* GET /transactions — List user's transactions

Admin Endpoints (JWT required, admin only)

* GET /admin/flagged — List all flagged (suspected fraud) transactions

Fraud Detection

Transactions with amounts greater than or equal to $10,000 are automatically flagged for review by admin users.

Data Persistence

This implementation uses in-memory storage (Python dictionaries) for users and transactions. All data will reset on server restart. For production use, integrate a database (e.g., PostgreSQL, MongoDB).

Future Improvements

* Persistent database backend
* Enhanced fraud detection algorithms
* Email notifications for flagged transactions
* Rate limiting and security hardening
* Frontend integration

License

MIT License
