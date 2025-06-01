from storage import get_all_users
from models import Transaction
from datetime import datetime, timedelta
from fraud_detection import detect_fraud 

def daily_fraud_scan():
    flagged_count = 0
    now = datetime.utcnow()
    all_transactions = []

    for user in get_all_users():
        if user.deleted:
            continue
        all_transactions.extend([tx for tx in user.transactions if not tx.flagged])

    flagged_transactions = detect_fraud(all_transactions)

    for flagged in flagged_transactions:
        tx = flagged['transaction']
        if not tx.flagged:
            tx.flagged = True
            flagged_count += 1
            mock_send_email_alert(tx.from_user or tx.to_user, tx, flagged['reason'])

    print(f"Daily fraud scan completed. Flagged transactions: {flagged_count}")

def mock_send_email_alert(username, transaction, reason):
    print(f"Alert Email: User {username} has a suspicious transaction {transaction.tx_id} flagged. Reason: {reason}")
