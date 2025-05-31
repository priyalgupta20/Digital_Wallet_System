from datetime import datetime
import uuid

class User:
    def __init__(self, username, hashed_pin, is_admin=False):
        self.username = username
        self.hashed_pin = hashed_pin
        self.balances = {}  # { 'USD': 100.0, 'EUR': 50.0, ... }
        self.transactions = []  # List of Transaction objects
        self.blocked = False
        self.is_admin = is_admin
        self.deleted = False

    def get_balance(self, currency='USD'):
        return self.balances.get(currency, 0.0)

    def update_balance(self, currency, amount):
        current = self.get_balance(currency)
        self.balances[currency] = current + amount

    def add_transaction(self, transaction):
        # Ensure full Transaction object is added, not just ID
        self.transactions.append(transaction)

class Transaction:
    def __init__(self, from_user, to_user, amount, currency='USD', tx_type='transfer', timestamp=None):
        self.tx_id = str(uuid.uuid4())  # Unique transaction ID
        self.from_user = from_user      # None for deposit
        self.to_user = to_user          # None for withdrawal
        self.amount = amount
        self.currency = currency
        self.tx_type = tx_type          # 'deposit', 'withdraw', 'transfer'
        self.timestamp = timestamp or datetime.utcnow()
        self.deleted = False            # For soft-deletes
        self.flagged = False            # For fraud detection
