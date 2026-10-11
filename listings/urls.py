from django.urls import path

from . import views

app_name = "listings"

urlpatterns = [
    path("properties/", views.catalog, name="catalog"),
    path("properties/<slug:slug>/", views.detail, name="detail"),
    path("s/<str:token>/", views.share, name="share"),
    path("inquiry/", views.submit_lead, name="lead"),
]
