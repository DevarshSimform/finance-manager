from django.urls import path
from group import views

urlpatterns = [
    path('groups/', views.GroupListCreateAPIView.as_view(), name="group-list-create"),
]
