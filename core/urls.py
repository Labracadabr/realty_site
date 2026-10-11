from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("how-to-buy/", views.how_to_buy, name="how_to_buy"),
    path("contact/", views.contact, name="contact"),
    path("p/<slug:slug>/", views.page, name="page"),
]
