from django.conf import settings
from django.dispatch import Signal
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from voybit_payment_gateway import Client, parse_event
from voybit_payment_gateway_django.webhook import status_code

webhook_received = Signal()


def gateway_client() -> Client:
    return Client(getattr(settings, "VOYBIT_API_KEY", "") or "")


@csrf_exempt
@require_POST
def webhook(request):
    raw = request.body
    code = status_code(
        getattr(settings, "VOYBIT_WEBHOOK_SECRET", "") or "",
        request.headers.get("Voybit-Webhook-Id", ""),
        request.headers.get("Voybit-Webhook-Timestamp", ""),
        request.headers.get("Voybit-Webhook-Signature", ""),
        raw,
    )
    if code != 204:
        return HttpResponse(status=401)
    try:
        event = parse_event(raw)
    except ValueError:
        return HttpResponse(status=400)
    webhook_received.send(sender=webhook, event=event)
    return HttpResponse(status=204)
