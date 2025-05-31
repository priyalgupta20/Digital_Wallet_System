from storage import get_all_users, add_transaction
from models import Transaction
from datetime import datetime, timedelta

def daily_fraud_scan():
    flagged_count = 0
    now = datetime.utcnow()
    for user in get_all_users():
        if user.deleted:
            continue
        # Check for large withdrawals in last 24h
        for tx in user.transactions:
            if tx.tx_type == 'withdraw' and not tx.flagged and (now - tx.timestamp) < timedelta(days=1):
                if tx.amount > 1000:  # threshold
                    tx.flagged = True
                    flagged_count += 1
                    mock_send_email_alert(user.username, tx)
    print(f"Daily fraud scan completed. Flagged transactions: {flagged_count}")

def mock_send_email_alert(username, transaction):
    # mock email alert function
    print(f"Alert Email: User {username} has a suspicious transaction {transaction.tx_id} flagged.")
