from django.urls import path
from . import views

app_name = "checkout"
urlpatterns = [
    path("address/", views.address_view, name="address"),
    path("confirm/", views.confirm_view, name="confirm"),
    path("done/", views.done_view, name="done"),
]
