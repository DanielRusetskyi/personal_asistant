import json, logging
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
from .models import PushSubscription
from accounts.models import UserSettings

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def push_status(request):
    us, _ = UserSettings.objects.get_or_create(user=request.user)
    has_sub = PushSubscription.objects.filter(user=request.user).exists()
    return JsonResponse({"enabled": us.push_enabled, "has_subscription": has_sub})


@never_cache
def vapid_public(request):
    return HttpResponse(settings.VAPID_PUBLIC_KEY_B64URL, content_type="text/plain")


@login_required
@require_POST
def push_toggle(request):
    try:
        body = json.loads(request.body.decode() or "{}")
        enabled = bool(body.get("enabled"))
        us, _ = UserSettings.objects.get_or_create(user=request.user)
        us.push_enabled = enabled
        us.save()
        if not enabled:
            # На вимкненні — видаляємо підписки, щоб гарантійно нічого не прийшло
            PushSubscription.objects.filter(user=request.user).delete()
        return JsonResponse({"ok": True, "enabled": us.push_enabled})
    except Exception as e:
        return HttpResponseBadRequest(str(e))


@login_required
@require_POST
def push_subscribe(request):
    try:
        body = json.loads(request.body.decode() or "{}")
        sub = body.get("subscription") or body  # приймемо обидва варіанти
        endpoint = sub.get("endpoint")
        keys = sub.get("keys") or {}
        if not endpoint or "p256dh" not in keys or "auth" not in keys:
            return HttpResponseBadRequest("Bad subscription")

        obj, created = PushSubscription.objects.update_or_create(
            user=request.user, endpoint=endpoint,
            defaults={
                "p256dh": keys["p256dh"],
                "auth": keys["auth"],
                "ua": request.META.get("HTTP_USER_AGENT", "")
            }
        )
        logger.info("Push subscribed user=%s created=%s", request.user.pk, created)
        return JsonResponse({"ok": True})
    except Exception as e:
        logger.exception("push_subscribe error")
        return HttpResponseBadRequest(str(e))


@login_required
@require_POST
def push_unsubscribe(request):
    try:
        body = json.loads(request.body.decode() or "{}")
        endpoint = (body.get("subscription") or body).get("endpoint")
        if endpoint:
            PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
        return JsonResponse({"ok": True})
    except Exception as e:
        return HttpResponseBadRequest(str(e))