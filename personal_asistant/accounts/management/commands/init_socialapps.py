from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = "Ініціалізація SocialApp для Google з env-змінних"

    def handle(self, *args, **options):
        site_id = int(os.getenv("SITE_ID", 1))
        domain = os.getenv("SITE_DOMAIN", "personal-asistant.fly.dev")
        name = os.getenv("SITE_NAME", "Personal Assistant")

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not client_id or not secret:
            self.stdout.write(self.style.ERROR("❌ GOOGLE_CLIENT_ID або GOOGLE_CLIENT_SECRET не задані у середовищі"))
            return

        site, _ = Site.objects.update_or_create(
            id=site_id,
            defaults={"domain": domain, "name": name},
        )

        app, created = SocialApp.objects.update_or_create(
            provider="google",
            defaults={
                "name": "Google",
                "client_id": client_id,
                "secret": secret,
            },
        )
        app.sites.set([site])
        app.save()

        if created:
            self.stdout.write(self.style.SUCCESS("✅ Створено SocialApp для Google"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ Оновлено SocialApp для Google"))
