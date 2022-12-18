from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('test_voting/', views.create_voting, name='test_create')
]
