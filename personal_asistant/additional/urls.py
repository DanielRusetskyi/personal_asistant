from django.urls import path
from . import views

app_name = "additional"

urlpatterns = [
    path("weather/", views.weather_view, name="weather"),
    path("radio/", views.PlayerView.as_view(), name="radio"),
    path("radio/stations", views.stations_json, name="stations"),
    path("radio/play/<slug:slug>", views.play_redirect, name="play"),
    path("rates/", views.rates_page, name="rates_page"),
    path("api/pb-currencies", views.pb_currencies_api, name="pb_currencies_api"),
    path("api/pb-rates/", views.pb_rates_api, name="pb_rates_api"),

]
