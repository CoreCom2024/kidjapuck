from django.urls import path
from . import views

app_name = "properties"

urlpatterns = [
    path("search/", views.search, name="search"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
]