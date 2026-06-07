from django import forms
from django.utils.html import format_html

class ImageCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
	template_name = "widgets/image_checkbox_select.html"
	option_template_name = "widgets/image_checkbox_option.html"

	def create_option(self, name, value, label, selected, index, subindex=None, attrs=None,):
		option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)

		image_obj = value.instance if hasattr(value, "instance") else None

		option["image_url"] = ""
		option["image_label"] = str(label)

		if image_obj:
			img = getattr(image_obj, "img", None)
			img_mini = getattr(image_obj, "img_mini", None)

			if img_mini:
				option["image_url"] = img_mini.url
			elif img:
				option["image_url"] = img.url

			option["image_label"] = (
				getattr(image_obj, "name", None)
				or getattr(image_obj, "alt_text", None)
				or str(label)
			)

		return option