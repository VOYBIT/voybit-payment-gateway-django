from voybit_payment_gateway import verify_webhook


def status_code(secret: str, delivery_id: str, timestamp: str, signature: str, raw_body: bytes) -> int:
    try:
        verify_webhook(secret, delivery_id, timestamp, signature, raw_body)
    except ValueError:
        return 401
    return 204
