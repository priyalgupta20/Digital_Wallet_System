from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from storage import get_user, get_flagged_transactions, get_all_users

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        username = get_jwt_identity()
        user = get_user(username)
        if not user or not user.is_admin:
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@admin_bp.route('/flagged-transactions', methods=['GET'])
@admin_required
def flagged_transactions():
    flagged = get_flagged_transactions()
    results = []
    for tx in flagged:
        results.append({
            'tx_id': tx.tx_id,
            'from_user': tx.from_user,
            'to_user': tx.to_user,
            'amount': tx.amount,
            'currency': tx.currency,
            'tx_type': tx.tx_type,
            'timestamp': tx.timestamp.isoformat(),
            'deleted': tx.deleted
        })
    return jsonify(results), 200

@admin_bp.route('/total-balances', methods=['GET'])
@admin_required
def total_balances():
    users = get_all_users()
    currency_totals = {}
    for user in users:
        for curr, amt in user.balances.items():
            currency_totals[curr] = currency_totals.get(curr, 0.0) + amt
    return jsonify(currency_totals), 200

@admin_bp.route('/top-users', methods=['GET'])
@admin_required
def top_users():
    users = get_all_users()
    sort_by = request.args.get('sort_by', 'balance') 
    currency = request.args.get('currency', 'USD')

    if sort_by == 'balance':
        sorted_users = sorted(users, key=lambda u: u.get_balance(currency), reverse=True)
    elif sort_by == 'volume':
        sorted_users = sorted(users, key=lambda u: sum(tx.amount for tx in u.transactions if tx.currency == currency), reverse=True)
    else:
        return jsonify({"msg": "Invalid sort_by parameter"}), 400

    result = []
    for user in sorted_users[:10]:
        total_volume = sum(tx.amount for tx in user.transactions if tx.currency == currency)
        result.append({
            'username': user.username,
            'balance': user.get_balance(currency),
            'transaction_volume': total_volume
        })

    return jsonify(result), 200
