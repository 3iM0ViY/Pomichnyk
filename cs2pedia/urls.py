from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
	path('', index, name = "home"),
	path('maps/', MapsListView.as_view(), name = "maps"),
	path("maps/<slug:slug>/", MapDetailView.as_view(), name="map_detail"),
	path("lineups/<int:pk>/vote/", lineup_vote, name="lineup_vote"),
]