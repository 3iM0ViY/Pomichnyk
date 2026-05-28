from django.shortcuts import render
from .models import *
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView
from django.db.models import F

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import *


# Create your views here.
def index(request):
	return render(request, "base.html")

class MapsListView(ListView):
	template_name = "maps.html"
	context_object_name = "pool_maps"

	def get_queryset(self):
		maps_in_pool = Map.objects.filter(is_published=True, is_in_pool=True)
		return (maps_in_pool)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context["other_maps"] = (Map.objects.filter(is_published=True, is_in_pool=False))

		return context

class MapDetailView(DetailView):
	model = Map
	template_name = "map_detail.html"
	context_object_name = "map"
	slug_field = "slug"
	slug_url_kwarg = "slug"

	def get_queryset(self):
		return (Map.objects.filter(is_published=True))

	def get_object(self, queryset=None):
		obj = super().get_object(queryset)

		# Atomic increment
		Map.objects.filter(pk=obj.pk).update(
			views=F("views") + 1
		)
		obj.refresh_from_db(fields=["views"])

		return obj

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		strategies = Strategy.objects.filter(mapa=self.object, is_active=True).select_related("created_by").order_by("-likes", "-created_at")[:10]
		lineups = Lineup.objects.filter(mapa=self.object, is_published=True).select_related("created_by").prefetch_related("slide").order_by("-likes", "-created_at")
		
		context.update({
			"strategies": strategies,
			"lineups": lineups,
		})

		return context

@require_POST
def lineup_vote(request, pk):
	lineup = get_object_or_404(Lineup, pk=pk, is_published=True)
	action = request.POST.get("vote")

	if action not in ["up", "down"]:
		return JsonResponse({"error": "Invalid vote"}, status=400)

	votes = request.session.get("lineup_votes", {})

	old_vote = votes.get(str(pk), 0)
	new_vote = 1 if action == "up" else -1

	# clicking same vote again removes it
	if old_vote == new_vote:
		new_vote = 0

	delta = new_vote - old_vote

	Lineup.objects.filter(pk=pk).update(
		likes=F("likes") + delta
	)

	lineup.refresh_from_db(fields=["likes"])

	if new_vote == 0:
		votes.pop(str(pk), None)
	else:
		votes[str(pk)] = new_vote

	request.session["lineup_votes"] = votes
	request.session.modified = True

	return JsonResponse({
		"likes": lineup.likes,
		"user_vote": new_vote,
	})

class StratDetailView(DetailView):
	model = Strategy
	template_name = "strat_detail.html"
	context_object_name = "strat"
	slug_field = "slug"
	slug_url_kwarg = "slug"

	def get_queryset(self):
		return (Strategy.objects.filter(is_active=True))


@require_POST
def strategy_vote(request, pk):
	strategy = get_object_or_404(Strategy, pk=pk, is_active=True)
	action = request.POST.get("vote")

	if action not in ["up", "down"]:
		return JsonResponse({"error": "Invalid vote"}, status=400)

	votes = request.session.get("strategy_votes", {})

	old_vote = votes.get(str(pk), 0)
	new_vote = 1 if action == "up" else -1

	# clicking same vote again removes it
	if old_vote == new_vote:
		new_vote = 0

	delta = new_vote - old_vote

	Strategy.objects.filter(pk=pk).update(
		likes=F("likes") + delta
	)

	strategy.refresh_from_db(fields=["likes"])

	if new_vote == 0:
		votes.pop(str(pk), None)
	else:
		votes[str(pk)] = new_vote

	request.session["strategy_votes"] = votes
	request.session.modified = True

	return JsonResponse({
		"likes": strategy.likes,
		"user_vote": new_vote,
	})



class RegisterView(CreateView):
	form_class = UserCreationForm
	template_name = "registration/register.html"
	success_url = reverse_lazy("pomichnyk_core:creator_dashboard")

	def form_valid(self, form):
		response = super().form_valid(form)
		login(self.request, self.object)
		return response


class CreatorDashboardView(LoginRequiredMixin, TemplateView):
	template_name = "creator/dashboard.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		strategies = self.request.user.creator_strategies.select_related("mapa").all()
		lineups = self.request.user.creator_lineups.select_related("mapa").all()
		
		context.update({
			"strategies": strategies,
			"lineups": lineups,
		})

		return context

# a reusable ownership mixin
class CreatorOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		obj = self.get_object()
		return obj.created_by == self.request.user

# User made stategies
class StrategyCreateView(LoginRequiredMixin, CreateView):
	model = Strategy
	form_class = StrategyForm
	template_name = "creator/strategy_form.html"

	def form_valid(self, form):
		form.instance.created_by = self.request.user
		return super().form_valid(form)

class StrategyUpdateView(CreatorOnlyMixin, UpdateView):
	model = Strategy
	form_class = StrategyForm
	template_name = "creator/strategy_form.html"

class StrategyDeleteView(CreatorOnlyMixin, DeleteView):
	model = Strategy
	template_name = "creator/strategy_confirm_delete.html"
	success_url = reverse_lazy("pomichnyk_core:creator_dashboard")

# User made lineups
class LineupCreateView(LoginRequiredMixin, CreateView):
	model = Lineup
	form_class = LineupForm
	template_name = "creator/lineup_form.html"

	def form_valid(self, form):
		form.instance.created_by = self.request.user
		return super().form_valid(form)

class LineupUpdateView(CreatorOnlyMixin, UpdateView):
	model = Lineup
	form_class = LineupForm
	template_name = "creator/lineup_form.html"

class LineupDeleteView(CreatorOnlyMixin, DeleteView):
	model = Lineup
	template_name = "creator/lineup_confirm_delete.html"
	success_url = reverse_lazy("pomichnyk_core:creator_dashboard")