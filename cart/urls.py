from django.urls import path
from . import views

app_name = "cart"
urlpatterns = [
    path("", views.cart_view, name="view"),
    path("add/<slug:slug>/", views.cart_add, name="add"),
    path("remove/<slug:slug>/", views.cart_remove, name="remove"),
    path("clear/", views.cart_clear, name="clear"),
    path("count/", views.cart_count, name="count"),
]
