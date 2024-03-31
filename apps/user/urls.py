from django.urls import path
from .views import (
    UserCenterView,
    LoginView,
    ModifyUserInfoView,
    ChangePasswordView,
    SelectedCourseInfoView,
)
from apps.homework.views import UploadView


app_name = 'user'

urlpatterns = [
    path('', UserCenterView.as_view(), name='center'),
    path('login', LoginView.as_view(), name='login'),
    path('upload', UploadView.as_view(), name='upload'),
    path('modify', ModifyUserInfoView.as_view(), name='modify'),
    path('change-password', ChangePasswordView.as_view(), name='change'),
    path('selected', SelectedCourseInfoView.as_view(), name='selected'),
]
