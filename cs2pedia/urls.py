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
	path("search/", global_search, name="global_search"),
	
	path("register/", RegisterView.as_view(), name="register"),
	path("creator/", CreatorDashboardView.as_view(), name="creator_dashboard"),

	path("creator/strats/new/", StrategyCreateView.as_view(), name="strategy_create"),
	path("creator/strats/<slug:slug>/edit/", StrategyUpdateView.as_view(), name="strategy_update"),
	path("creator/strats/<slug:slug>/delete/", StrategyDeleteView.as_view(), name="strategy_delete"),
	path("creator/lineups/new/", LineupCreateView.as_view(), name="lineup_create"),
	path("creator/lineups/<int:pk>/edit/", LineupUpdateView.as_view(), name="lineup_update"),
	path("creator/lineups/<int:pk>/delete/", LineupDeleteView.as_view(), name="lineup_delete"),
]