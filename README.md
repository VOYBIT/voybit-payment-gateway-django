# Voybit payment gateway for Django

## Get an API key

1. Create an account at [dashboard.voybit.com](https://dashboard.voybit.com).
2. Open **Gateways**, create a payment gateway, enable the assets customers may choose, and store its webhook secret as `VOYBIT_WEBHOOK_SECRET`.
3. Open **API keys**, choose **Create secret key**, and bind it to that gateway. Copy the full `vb_live_…` value once and store it as `VOYBIT_API_KEY` on your server.

Create a buyer-choice checkout session and verify its webhook with the [Python library](https://github.com/VOYBIT/voybit-payment-gateway-python). The API key and webhook secret stay in Django settings.

```bash
pip install "voybit-payment-gateway-django @ git+https://github.com/VOYBIT/voybit-payment-gateway-django.git"
```

Not published to PyPI.

```python
VOYBIT_API_KEY = os.environ["VOYBIT_API_KEY"]
VOYBIT_WEBHOOK_SECRET = os.environ["VOYBIT_WEBHOOK_SECRET"]
```

Add `voybit_payment_gateway_django` to `INSTALLED_APPS`. Create a checkout session with `gateway_client()` and send the payer to `checkout_url`.

```python
from django.urls import path
from voybit_payment_gateway_django.views import webhook

urlpatterns = [
    path("webhooks/voybit", webhook, name="voybit-webhook"),
]
```

The view is exempt from CSRF. It checks the signature, then sends `webhook_received` with `event`. Fulfil only when `status` is `paid` or `overpaid`, and ignore a repeated `Voybit-Webhook-Id`.

```python
from voybit_payment_gateway_django.views import webhook_received

def fulfil(sender, event, **kwargs):
    if event.get("status") not in ("paid", "overpaid"):
        return

webhook_received.connect(fulfil)
```
