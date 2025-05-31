from models import User, Transaction
import threading

_users = {}       
_transactions = {}
_lock = threading.Lock()

def add_user(user):
    with _lock:
        if user.username in _users:
            raise ValueError("Username already exists")
        _users[user.username] = user

def get_user(username):
    return _users.get(username)

def get_all_users():
    return [u for u in _users.values() if not u.deleted]

def add_transaction(tx):
    with _lock:
        _transactions[tx.tx_id] = tx

def get_transaction(tx_id):
    return _transactions.get(tx_id)

def get_all_transactions():
    return [tx for tx in _transactions.values() if not tx.deleted]

def get_flagged_transactions():
    return [tx for tx in _transactions.values() if tx.flagged and not tx.deleted]

def soft_delete_user(username):
    user = _users.get(username)
    if user:
        user.deleted = True

def soft_delete_transaction(tx_id):
    tx = _transactions.get(tx_id)
    if tx:
        tx.deleted = True
