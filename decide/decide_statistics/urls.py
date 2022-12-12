from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    #path('<int:voting_id>/<str:graph_type>', views.showVoting, name="showVoting"),
]
