from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PushSubscription


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "noteapp/settings.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            ctx['return_url'] = referer
        # Чи вже є хоч одна підписка у цього користувача
        ctx["has_push"] = PushSubscription.objects.filter(user=self.request.user).exists()
        return ctx
