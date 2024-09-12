from django.urls import path, include
from rest_framework import routers

from account.api import views




# router = routers.DefaultRouter()
# router.register('users', views.UserView, basename="user")



urlpatterns = [
    path('register/', views.registration_view, name='register_api'),
    path('flag_user/<str:user>', views.flag_uses, name='flag_user'),
    # path('', include(router.urls))
]