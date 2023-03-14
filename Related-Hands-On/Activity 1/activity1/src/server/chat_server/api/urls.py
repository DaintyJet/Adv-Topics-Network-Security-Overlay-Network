from .views import register_view, login_view, user_info_view
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('register', register_view),
    path('login', login_view),
    path('userinfo', user_info_view),
]

urlpatterns = format_suffix_patterns(urlpatterns)
