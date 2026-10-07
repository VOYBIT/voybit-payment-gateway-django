import hashlib
import hmac
import time
import unittest

from voybit_payment_gateway_django.webhook import status_code


def sign(secret: str, delivery_id: str, timestamp: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), f"{delivery_id}.{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return "v1=" + digest


class WebhookTests(unittest.TestCase):
    def test_accepts_a_fresh_signature(self):
        body = b'{"id":"evt_1","type":"payment.paid","status":"paid"}'
        timestamp = str(int(time.time()))
        signature = sign("whsec_test", "evt_1", timestamp, body)
        self.assertEqual(status_code("whsec_test", "evt_1", timestamp, signature, body), 204)

    def test_rejects_a_bad_signature(self):
        body = b'{"status":"paid"}'
        timestamp = str(int(time.time()))
        self.assertEqual(status_code("whsec_test", "evt_1", timestamp, "v1=" + "ab" * 32, body), 401)


if __name__ == "__main__":
    unittest.main()
