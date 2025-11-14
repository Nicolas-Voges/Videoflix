from django.urls import path

from .views import RegisterAPIView, ActivationAPIView, LoginTokenObtainPairView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name="register"),
    path('activate/<str:uidb64>/<str:token>/', ActivationAPIView.as_view(), name="activate"),
    path('login/', LoginTokenObtainPairView.as_view(), name="login"),
]