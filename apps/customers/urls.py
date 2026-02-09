from django.urls import path
from .views import CustomerRegistrationView

urlpatterns = [
    path('register', CustomerRegistrationView.as_view(), name='register-customer'),
]
