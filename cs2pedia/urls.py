from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
	path('', index, name = "home"),
	path('maps/', MapsListView.as_view(), name = "maps"),
	path("maps/<slug:slug>/", MapDetailView.as_view(), name="map_detail"),
	path("lineups/<int:pk>/vote/", lineup_vote, name="lineup_vote"),
	path("strats/<slug:slug>/", StratDetailView.as_view(), name="strat_detail"),
	path("strats/<int:pk>/vote/", strategy_vote, name="strategy_vote"),
]