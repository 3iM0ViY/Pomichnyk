from django import forms
from .models import Strategy, Lineup


class StrategyForm(forms.ModelForm):
	class Meta:
		model = Strategy
		fields = [
			"mapa",
			"name",
			"slug",
			"side",
			"description",
			"slide",
			"is_active",
		]


class LineupForm(forms.ModelForm):
	class Meta:
		model = Lineup
		fields = [
			"mapa",
			"title",
			"description",
			"comment",
			"utility",
			"throw_from",
			"land_at",
			"slide",
			"video_url",
			"is_published",
		]