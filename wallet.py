from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from storage import get_user, add_transaction, get_all_transactions
from models import Transaction
from datetime import datetime

wallet_bp = Blueprint('wallet', __name__)

FRAUD_THRESHOLD = 10000.0
TRANSFER_LIMIT_COUNT = 3
TRANSFER_TIME_WINDOW = 60  # seconds
WITHDRAWAL_RATIO_LIMIT = 0.8


def check_and_flag_fraud(tx):
    now = tx.timestamp

    # Flag if amount exceeds threshold
    if tx.amount >= FRAUD_THRESHOLD:
        tx.flagged = True
        print(f"Large transaction flagged: {tx.amount}")

    # Flag multiple quick transfers
    if tx.tx_type == "transfer":
        recent = [
            t for t in get_all_transactions()
            if t.from_user == tx.from_user
            and t.tx_type == "transfer"
            and (now - t.timestamp).total_seconds() < TRANSFER_TIME_WINDOW
        ]
        if len(recent) >= TRANSFER_LIMIT_COUNT:
            tx.flagged = True
            print(f"Multiple quick transfers flagged for {tx.from_user}")

    # Flag large withdrawals
    if tx.tx_type == "withdraw":
        user = get_user(tx.from_user)
        original_balance = user.get_balance(tx.currency) + tx.amount
        if original_balance > 0 and tx.amount / original_balance > WITHDRAWAL_RATIO_LIMIT:
            tx.flagged = True
            print(f"Large withdrawal flagged for {tx.from_user}")


@wallet_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    username = get_jwt_identity()
    currency = request.args.get('currency', 'USD')
    user = get_user(username)

    if not user or user.deleted or user.blocked:
        return jsonify({"msg": "User not found or blocked"}), 404

    balance = user.get_balance(currency)
    return jsonify({
        "username": username,
        "currency": currency,
        "balance": balance
    }), 200


@wallet_bp.route('/deposit', methods=['POST'])
@jwt_required()
def deposit():
    username = get_jwt_identity()
    data = request.get_json()
    amount = data.get('amount')
    currency = data.get('currency', 'USD')

    if amount is None or amount <= 0:
        return jsonify({"msg": "Invalid amount"}), 400

    user = get_user(username)
    if not user or user.deleted or user.blocked:
        return jsonify({"msg": "User not found or blocked"}), 404

    user.update_balance(currency, amount)

    tx = Transaction(
        from_user=None,
        to_user=username,
        amount=amount,
        currency=currency,
        tx_type='deposit',
        timestamp=datetime.utcnow()
    )
    check_and_flag_fraud(tx)

    add_transaction(tx)
    user.add_transaction(tx)

    return jsonify({
        "msg": "Deposit successful",
        "transaction_id": tx.tx_id,
        "flagged": tx.flagged
    }), 201


@wallet_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    username = get_jwt_identity()
    data = request.get_json()
    amount = data.get('amount')
    currency = data.get('currency', 'USD')

    if amount is None or amount <= 0:
        return jsonify({"msg": "Invalid amount"}), 400

    user = get_user(username)
    if not user or user.deleted or user.blocked:
        return jsonify({"msg": "User not found or blocked"}), 404

    if user.get_balance(currency) < amount:
        return jsonify({"msg": "Insufficient funds"}), 400

    user.update_balance(currency, -amount)

    tx = Transaction(
        from_user=username,
        to_user=None,
        amount=amount,
        currency=currency,
        tx_type='withdraw',
        timestamp=datetime.utcnow()
    )
    check_and_flag_fraud(tx)

    add_transaction(tx)
    user.add_transaction(tx)

    return jsonify({
        "msg": "Withdrawal successful",
        "transaction_id": tx.tx_id,
        "flagged": tx.flagged
    }), 201


@wallet_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    from_username = get_jwt_identity()
    data = request.get_json()
    to_username = data.get('to_username')
    amount = data.get('amount')
    currency = data.get('currency', 'USD')

    if not to_username or amount is None or amount <= 0:
        return jsonify({"msg": "Missing or invalid transfer data"}), 400

    if to_username == from_username:
        return jsonify({"msg": "Cannot transfer to self"}), 400

    from_user = get_user(from_username)
    to_user = get_user(to_username)

    if not from_user or from_user.deleted or from_user.blocked:
        return jsonify({"msg": "Sender not found or blocked"}), 404
    if not to_user or to_user.deleted or to_user.blocked:
        return jsonify({"msg": "Recipient not found or blocked"}), 404

    if from_user.get_balance(currency) < amount:
        return jsonify({"msg": "Insufficient funds"}), 400

    from_user.update_balance(currency, -amount)
    to_user.update_balance(currency, amount)

    tx = Transaction(
        from_user=from_username,
        to_user=to_username,
        amount=amount,
        currency=currency,
        tx_type='transfer',
        timestamp=datetime.utcnow()
    )
    check_and_flag_fraud(tx)

    add_transaction(tx)
    from_user.add_transaction(tx)
    to_user.add_transaction(tx)

    return jsonify({
        "msg": "Transfer successful",
        "transaction_id": tx.tx_id,
        "flagged": tx.flagged
    }), 201


@wallet_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    username = get_jwt_identity()
    user = get_user(username)
    if not user or user.deleted or user.blocked:
        return jsonify({"msg": "User not found or blocked"}), 404

    # Filter all transactions to those linked to this user
    user_tx_ids = {tx.tx_id for tx in user.transactions}
    transactions = [tx for tx in get_all_transactions() if tx.tx_id in user_tx_ids]

    # Serialize transactions for response
    tx_list = []
    for tx in transactions:
        tx_list.append({
            'tx_id': tx.tx_id,
            'from_user': tx.from_user,
            'to_user': tx.to_user,
            'amount': tx.amount,
            'currency': tx.currency,
            'tx_type': tx.tx_type,
            'timestamp': tx.timestamp.isoformat(),
            'flagged': tx.flagged,
            'deleted': tx.deleted
        })

    return jsonify(tx_list), 200


@wallet_bp.route('/admin/flagged', methods=['GET'])
@jwt_required()
def get_flagged_transactions():
    username = get_jwt_identity()
    user = get_user(username)
    if not user or not user.is_admin:
        return jsonify({"msg": "Unauthorized"}), 403

    flagged = [tx for tx in get_all_transactions() if tx.flagged]
    flagged_list = []
    for tx in flagged:
        flagged_list.append({
            'tx_id': tx.tx_id,
            'from_user': tx.from_user,
            'to_user': tx.to_user,
            'amount': tx.amount,
            'currency': tx.currency,
            'tx_type': tx.tx_type,
            'timestamp': tx.timestamp.isoformat(),
            'flagged': tx.flagged,
            'deleted': tx.deleted
        })
    return jsonify(flagged_list), 200
