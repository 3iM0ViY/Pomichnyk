from django.shortcuts import render
from .models import *
from django.views.generic import ListView, DetailView
from django.db.models import F

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

		context["other_maps"] = (
			Map.objects
			.filter(
				is_published=True,
				is_in_pool=False
			)
		)

		return context

class MapDetailView(DetailView):
	model = Map
	template_name = "map_detail.html"
	context_object_name = "map"
	slug_field = "slug"
	slug_url_kwarg = "slug"

	def get_queryset(self):
		return (
			Map.objects
			.filter(is_published=True)
		)

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

		context["related_maps"] = (
			Map.objects
			.filter(
				is_published=True,
				is_in_pool=self.object.is_in_pool
			)
			.exclude(pk=self.object.pk)
			[:4]
		)

		return context