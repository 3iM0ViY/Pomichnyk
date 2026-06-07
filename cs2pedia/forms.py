from django import forms
from .models import *
from django.forms import modelformset_factory
from .widgets import ImageCheckboxSelectMultiple

class StrategyForm(forms.ModelForm):
	slide = forms.ModelMultipleChoiceField(
		queryset=StratImg.objects.all(),
		required=False,
		widget=ImageCheckboxSelectMultiple(attrs={
			"class": "media-picker-source",
		}),
		label="Зображення",
	)

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
		widgets = {
			"slide": forms.CheckboxSelectMultiple,
		}

class LineupForm(forms.ModelForm):
	slide = forms.ModelMultipleChoiceField(
		queryset=LineupImg.objects.all(),
		required=False,
		widget=ImageCheckboxSelectMultiple(attrs={
			"class": "media-picker-source",
		}),
		label="Зображення",
	)
	
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
		widgets = {
			"slide": forms.CheckboxSelectMultiple,
		}

class StratImgUploadForm(forms.ModelForm):
	class Meta:
		model = StratImg
		fields = ["img", "name", "alt_text", "comment",]

class LineupImgUploadForm(forms.ModelForm):
	class Meta:
		model = LineupImg
		fields = ["img", "name", "alt_text", "comment",]

StratImgUploadFormSet = modelformset_factory(
	StratImg,
	form=StratImgUploadForm,
	extra=1,
	can_delete=True,
)

LineupImgUploadFormSet = modelformset_factory(
	LineupImg,
	form=LineupImgUploadForm,
	extra=1,
	can_delete=True,
)