# noteapp/push_send.py
import json, logging
from django.conf import settings
from django.utils import timezone
from pywebpush import webpush, WebPushException
from .models import PushSubscription

log = logging.getLogger(__name__)


def send_web_push_to_user(user, payload: dict, *, ttl=60, urgency="normal", topic=None):
    subs = list(PushSubscription.objects.filter(user=user).values("id", "endpoint", "p256dh", "auth"))
    if not subs:
        log.info("No push subs for user=%s", user.pk)
        return 0, 0

    vapid_key_for_webpush = settings.VAPID_PRIVATE_KEY_B64URL

    ok = fail = 0
    for s in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": s["endpoint"],
                    "keys": {"p256dh": s["p256dh"], "auth": s["auth"]},
                },
                data=json.dumps(payload),
                vapid_private_key=vapid_key_for_webpush,
                vapid_claims={"sub": settings.PUSH_SUBJECT},
                ttl=ttl,
                headers={k: v for k, v in {"Urgency": urgency, "Topic": topic}.items() if v},
            )
            PushSubscription.objects.filter(id=s["id"]).update(
                last_success_at=timezone.now(), last_error=""
            )
            ok += 1
        except WebPushException as e:
            status = getattr(e.response, "status_code", None)
            log.warning("Push failed endpoint=%s status=%s err=%s", s["endpoint"], status, e)
            if status in (404, 410):  # протухла підписка
                PushSubscription.objects.filter(id=s["id"]).delete()
            else:
                PushSubscription.objects.filter(id=s["id"]).update(last_error=str(e))
            fail += 1
        except Exception as e:
            log.exception("Push error endpoint=%s", s["endpoint"])
            fail += 1
    return ok, fail
