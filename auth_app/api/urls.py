from django.urls import path

from .views import RegisterView, ActivationView

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('activate/<str:uidb64>/<str:token>/', ActivationView.as_view(), name="activate"),
]