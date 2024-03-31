from django.urls import path
from .views import IndexView

app_name = 'course'

urlpatterns = [
    path("", IndexView.index_view, name='index'),
]
