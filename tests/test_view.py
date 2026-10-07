import hashlib
import hmac
import time
import unittest

import django
from django.conf import settings
from django.test import RequestFactory

if not settings.configured:
    settings.configure(SECRET_KEY="test", VOYBIT_WEBHOOK_SECRET="whsec_test")
    django.setup()

from voybit_payment_gateway_django.views import webhook


def sign(secret, delivery_id, timestamp, body):
    digest = hmac.new(secret.encode(), f"{delivery_id}.{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return "v1=" + digest


class ViewTests(unittest.TestCase):
    def test_view_accepts_a_signed_body(self):
        body = b'{"id":"evt_1","type":"payment.paid","status":"paid"}'
        timestamp = str(int(time.time()))
        request = RequestFactory().post(
            "/webhooks/voybit",
            data=body,
            content_type="application/json",
            HTTP_VOYBIT_WEBHOOK_ID="evt_1",
            HTTP_VOYBIT_WEBHOOK_TIMESTAMP=timestamp,
            HTTP_VOYBIT_WEBHOOK_SIGNATURE=sign("whsec_test", "evt_1", timestamp, body),
        )
        response = webhook(request)
        self.assertEqual(response.status_code, 204)

    def test_view_rejects_a_bad_signature(self):
        body = b'{"status":"paid"}'
        request = RequestFactory().post(
            "/webhooks/voybit",
            data=body,
            content_type="application/json",
            HTTP_VOYBIT_WEBHOOK_ID="evt_1",
            HTTP_VOYBIT_WEBHOOK_TIMESTAMP=str(int(time.time())),
            HTTP_VOYBIT_WEBHOOK_SIGNATURE="v1=" + "ab" * 32,
        )
        response = webhook(request)
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
