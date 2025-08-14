import os
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_socialapp_and_site(sender, **kwargs):
    """Автоініціалізація SocialApp(Google) + Site після міграцій у DEV/локально."""
    # Працюємо лише в DEV або якщо явно дозволено
    if not (getattr(settings, "DEBUG", False) or os.getenv("AUTO_INIT_SOCIAL") == "1"):
        return

    # Потрібні ключі — інакше пропускаємо без падіння
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not secret:
        return

    try:
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp
    except Exception as e:
        print(e)
        # Якщо пакети ще не готові (на ранніх етапах) — тихо виходимо
        return

    # Визначаємо домен і ім’я сайту для локалки
    site_id = int(os.getenv("SITE_ID", getattr(settings, "SITE_ID", 1)))
    domain = os.getenv("SITE_DOMAIN", "localhost:8000")
    name = os.getenv("SITE_NAME", "Personal Assistant")

    site, _ = Site.objects.update_or_create(
        id=site_id,
        defaults={"domain": domain, "name": name},
    )

    app, _ = SocialApp.objects.update_or_create(
        provider="google",
        defaults={
            "name": "Google",
            "client_id": client_id,
            "secret": secret,
        },
    )
    app.sites.set([site])
    app.save()
