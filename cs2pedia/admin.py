from django.contrib import admin
from .models import *

from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin

# Register your models here.

# Порядок виводу моделей в адмінці
original_get_app_list = admin.site.get_app_list
def custom_get_app_list(self, request, app_label=None):
    app_list = original_get_app_list(request, app_label)

    model_order = {
        "Map": 1,
        "Strategy": 2,
        "StratImg": 3,
        "Lineup": 4,
        "LineupImg": 5,
    }

    for app in app_list:
        if app["app_label"] == "cs2pedia":
            app["models"].sort(
                key=lambda x: model_order.get(x["object_name"], 999)
            )

    return app_list

def creator_display(creator_path="creator"):
	"""
	Створення посилання на користувача в 
		list_display = (... "creator_link", ...)
	для моделі з різним шляхом до поля creator=models.ForeignKey
	"""
	def decorator(admin_class):
		def get_creator(obj):
			value = obj
			for attr in creator_path.split("."):
				value = getattr(value, attr)
			return value

		def creator_link(self, obj):
			if not get_creator(obj):
				return "-"
			
			url = reverse(
				f"admin:{get_creator(obj)._meta.app_label}_{get_creator(obj)._meta.model_name}_change",
				args=[get_creator(obj).pk],
			)
			return format_html('<a href="{}">{}</a>', url, get_creator(obj))

		admin_class.creator_link = creator_link
		admin_class.creator_link.short_description = "Користувач"
		admin_class.creator_link.admin_order_field = "created_by"

		return admin_class
	return decorator

class MapAdmin(admin.ModelAdmin):
	fieldsets = (
		("Основне", {
			"fields": ("name", ("slug", "meta", "keywords",),)
		}),
		("Коллаути", {
			"fields": ("image", "img_mini", "get_photo", "alt_text",)
		}),
		("Стан", {
			"classes": ["collapse"],
			"fields": ("is_in_pool", ("views", "is_published", "created_at",), )
		}),
	)
	list_display = ("id", "name", "get_photo", "views", "is_in_pool", "is_published",)
	list_display_links = ("name",)
	list_editable = ("is_in_pool", "is_published",)
	list_filter = ("is_in_pool", "is_published",)
	search_fields = ("name", "meta", "keywords",)
	prepopulated_fields = {'slug': ('name',)}
	readonly_fields = ("get_photo", "views", "created_at",)
	show_facets = admin.ShowFacets.ALWAYS

	def get_photo(self, obj):
		if obj.img_mini:
			return mark_safe(f'<img src="{obj.img_mini.url}" width="50">') # об'єкт це посилання на модель з фотографією
		return "-"

	get_photo.short_description = "Зображення"

class StratImgAdmin(admin.ModelAdmin):
	list_display = ("id", "alt_text", "get_photo", "created_at")
	list_display_links = ("id",)
	list_editable = ("alt_text",)
	search_fields = ("alt_text",)
	readonly_fields = ("get_photo", "created_at",)
	fields = ("img", "img_mini", "alt_text", "get_photo", "created_at",)

	def get_photo(self, obj):
		if obj.img_mini:
			return mark_safe(f'<img src="{obj.img_mini.url}" width="50">') # об'єкт це посилання на модель з фотографією
		return "-"

	get_photo.short_description = "Зображення"

	# def has_module_permission(self, request):
	# 	return False # Приховати в сайдбарі адмінки

class StratImgInline(admin.TabularInline):
	model = Strategy.slide.through
	extra = 1
	insert_after = "description"

	readonly_fields = ("get_photo",)

	def get_photo(self, obj):
		img = getattr(obj, "stratimg", None)
		if img and img.img_mini:
			return mark_safe(f'<img src="{img.img_mini.url}" width="50">') # об'єкт це посилання на модель з фотографією
		return "-"

	get_photo.short_description = "Зображення"

@creator_display("created_by")
class StrategyAdmin(admin.ModelAdmin):
	fieldsets = (
		("Основне", {
			"fields": ("mapa", "name", "side")
		}),
		("Контент", {
			"fields": ("description",)
		}),
		("Стан", {
			"classes": ["collapse"],
			"fields": ("is_active", ("likes", "created_by", "created_at",), )
		}),
	)
	list_display = ("id", "name", "mapa", "side", "likes", "creator_link", "is_active")
	list_display_links = ("name",)
	list_editable = ("is_active",)
	list_filter = ("mapa", "side", "is_active")
	search_fields = ("name", "description",)
	readonly_fields = ("likes", "created_by", "created_at",)
	show_facets = admin.ShowFacets.ALWAYS

	inlines = [StratImgInline]

	change_form_template = 'admin/strategy_changeform.html'

	class Media:
		css = {
			'all': (
				'css/admin.css',
			)
		}

	def save_model(self, request, obj, form, change):
		if not change:  # only on creation
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

class LineupImgAdmin(admin.ModelAdmin):
	list_display = ("id", "alt_text", "get_photo", "created_at")
	list_display_links = ("id",)
	list_editable = ("alt_text",)
	search_fields = ("alt_text",)
	readonly_fields = ("get_photo", "created_at",)
	fields = ("img", "img_mini", "alt_text", "get_photo", "created_at",)

	def get_photo(self, obj):
		if obj.img_mini:
			return mark_safe(f'<img src="{obj.img_mini.url}" width="50">') # об'єкт це посилання на модель з фотографією
		return "-"

	get_photo.short_description = "Зображення"

	# def has_module_permission(self, request):
	# 	return False # Приховати в сайдбарі адмінки

class LineupImgInline(admin.TabularInline):
	model = Lineup.slide.through
	extra = 1
	insert_after = "land_at"
	readonly_fields = ("get_photo",)

	def get_photo(self, obj):
		img = getattr(obj, "lineupimg", None)
		if img and img.img_mini:
			return mark_safe(f'<img src="{img.img_mini.url}" width="50">') # об'єкт це посилання на модель з фотографією
		return "-"

	get_photo.short_description = "Зображення"

@creator_display("created_by")
class LineupAdmin(admin.ModelAdmin):
	fieldsets = (
		("Основне", {
			"fields": ("mapa", "title", "utility",)
		}),
		("Контент", {
			"fields": ("description", "comment", "throw_from", "land_at", )
		}),
		("Стан", {
			"classes": ["collapse"],
			"fields": ("is_published", ("likes", "created_by", "created_at",), )
		}),
	)
	list_display = ("id", "title", "mapa", "utility", "likes", "creator_link", "is_published")
	list_display_links = ("title",)
	list_editable = ("is_published",)
	list_filter = ("mapa", "utility", "is_published")
	search_fields = ("title", "throw_from", "land_at")
	readonly_fields = ("likes", "created_by", "created_at",)
	# fields = ("mapa", "title", "description", "comment", "utility", "throw_from", "land_at", "video_url", "likes", "is_published", "created_by", "created_at",)
	show_facets = admin.ShowFacets.ALWAYS

	inlines = [LineupImgInline]

	change_form_template = 'admin/strategy_changeform.html'

	class Media:
		css = {
			'all': (
				'css/admin.css',
			)
		}

	def save_model(self, request, obj, form, change):
		if not change:  # only on creation
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

admin.site.get_app_list = custom_get_app_list.__get__(admin.site, admin.AdminSite)
admin.site.register(Map, MapAdmin)
admin.site.register(Strategy, StrategyAdmin)
admin.site.register(StratImg, StratImgAdmin)
admin.site.register(Lineup, LineupAdmin)
admin.site.register(LineupImg, LineupImgAdmin)