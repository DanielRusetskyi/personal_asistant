from django.conf import settings
from urllib.parse import urlsplit, urlunsplit
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse, resolve, Resolver404
from django.utils.translation import override
from django.middleware.csrf import get_token
from preferences.services import (
    get_or_create_user_settings,
    set_language as set_lang,
    set_theme,
    set_compact,
    set_push_enabled
)
from noteapp.models import PushSubscription


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "preferences/settings.html"

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx["settings"] = get_or_create_user_settings(self.request.user)
        ctx['active_menu'] = 'settings'
        return ctx


class LanguagePageView(LoginRequiredMixin, TemplateView):
    template_name = "preferences/language.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # куди повертатися після зміни мови
        ctx["next"] = (
                self.request.GET.get("next")
                or self.request.META.get("HTTP_REFERER")
                or self.request.path
        )
        ctx['active_menu'] = 'settings'
        ctx['active_page'] = 'language'
        return ctx


class UpdateLanguageView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponseRedirect(reverse("preferences:language"))

    def post(self, request):
        lang = (request.POST.get("language") or "").lower()
        allowed = {code for code, _ in settings.LANGUAGES}

        # куди вертатися (бажано GET-сторінка)
        nxt = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("preferences:language")
        if lang not in allowed:
            return HttpResponseRedirect(nxt)

        set_lang(request.user, lang)

        parts = urlsplit(nxt)
        path_only = parts.path
        try:
            match = resolve(path_only)
            with override(lang):
                new_path = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
            # зберегти query/fragment
            nxt = urlunsplit((parts.scheme, parts.netloc, new_path, parts.query, parts.fragment))
        except Resolver404:
            # якщо шлях не розвʼязався — запасний варіант
            with override(lang):
                nxt = reverse("preferences:language")

        resp = HttpResponseRedirect(nxt)
        resp.set_cookie("django_language", lang, max_age=365*24*60*60)
        get_token(request)
        return resp


class UpdateThemeView(LoginRequiredMixin, View):
    def post(self, request):
        theme = request.POST.get("theme")
        if theme not in ("auto","light","dark"):
            return HttpResponseBadRequest("Invalid theme")
        set_theme(request.user, theme)
        return JsonResponse({"ok": True})


class UpdateCompactView(LoginRequiredMixin, View):
    def post(self, request):
        value = request.POST.get("compact") in ("1","true","on","yes")
        set_compact(request.user, value)
        return JsonResponse({"ok": True, "compact": value})


# class UpdatePushEnabledView(LoginRequiredMixin, View):
#     def post(self, request):
#         value = request.POST.get("enabled") in ("1","true","on","yes")
#         set_push_enabled(request.user, value)
#         return JsonResponse({"ok": True, "enabled": value})


class UpdatePushEnabledView(LoginRequiredMixin, TemplateView):
    template_name = "preferences/update_push.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            ctx['return_url'] = referer
        ctx['active_menu'] = 'settings'
        ctx['active_page'] = 'push_update'
        # Чи вже є хоч одна підписка у цього користувача
        ctx["has_push"] = PushSubscription.objects.filter(user=self.request.user).exists()
        return ctx
