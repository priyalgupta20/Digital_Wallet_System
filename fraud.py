from datetime import timedelta

FRAUD_AMOUNT_THRESHOLD = 10000.0  # ₹10,000 threshold
FRAUD_TX_FREQ_THRESHOLD = 3
FRAUD_TIME_WINDOW = timedelta(minutes=1)

def detect_fraud(transactions):
    flagged = []

    for tx in transactions:
        if tx.amount > FRAUD_AMOUNT_THRESHOLD:
            flagged.append({
                'id': tx.tx_id,
                'reason': f'High amount transaction > ₹{FRAUD_AMOUNT_THRESHOLD} in {tx.currency}',
                'transaction': tx
            })

    user_tx_map = {}
    for tx in transactions:
        users = [tx.from_user, tx.to_user]
        for user in users:
            if user:
                user_tx_map.setdefault(user, []).append(tx)

    for user, tx_list in user_tx_map.items():
        tx_list.sort(key=lambda x: x.timestamp)

        start = 0
        for end in range(len(tx_list)):
            while (tx_list[end].timestamp - tx_list[start].timestamp) > FRAUD_TIME_WINDOW:
                start += 1
            window_size = end - start + 1
            if window_size > FRAUD_TX_FREQ_THRESHOLD:
                flagged.append({
                    'id': tx_list[end].tx_id,
                    'reason': f'More than {FRAUD_TX_FREQ_THRESHOLD} transactions in {FRAUD_TIME_WINDOW} by user {user}',
                    'transaction': tx_list[end]
                })
                break 

    return flagged
