from django.db import models
from django.conf import settings
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify
import os
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile

# Create your models here.

def clean_image_name(instance, filename):
	original_name, ext = os.path.splitext(filename)
	ext = ext.lower()

	if instance.name:
		base_name = slugify(instance.name, allow_unicode=True).replace("-", "_")
	else:
		base_name = slugify(original_name, allow_unicode=True).replace("-", "_")

	return base_name, ext

@deconstructible
class ImageUploadTo:
	def __init__(self, path, suffix=""):
		self.path = path.rstrip("/")
		self.suffix = suffix

	def __call__(self, instance, filename):
		base_name, ext = clean_image_name(instance, filename)
		return f"{self.path}/{base_name}{self.suffix}{ext}"

def build_renamed_image_path(old_path, new_name, suffix=""):
	directory = os.path.dirname(old_path)
	_, ext = os.path.splitext(old_path)

	base_name = slugify(new_name, allow_unicode=True).replace("-", "_")

	return f"{directory}/{base_name}{suffix}{ext.lower()}"


class Map(models.Model):
	name = models.CharField(verbose_name='Назва', max_length=100)

	slug = models.SlugField(verbose_name='Слаг', unique=True)
	meta = models.CharField(verbose_name="Мета", max_length=250, blank=True, null=True)
	keywords = models.CharField(verbose_name="Ключові слова", max_length=250, blank=True, null=True)

	image = models.ImageField(verbose_name='Мапа', upload_to="cs2pedia/maps/")
	img_mini = models.ImageField(verbose_name='Стиснута мапа', upload_to="cs2pedia/maps/mini/", null=True, blank=True)
	alt_text = models.CharField(verbose_name="Підпис", max_length=250, null=True, blank=True)

	views = models.PositiveIntegerField(default=0, verbose_name="Кількість переглядів")
	is_in_pool = models.BooleanField(verbose_name='В мап-пулі', default=True)
	is_published = models.BooleanField(verbose_name='Опублікувати', default=True)

	created_at = models.DateTimeField(verbose_name='Створено', auto_now_add=True, null=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Мапа'
		verbose_name_plural = 'Мапи'
		ordering = ["-is_published", "-is_in_pool", 'name']

	def get_absolute_url(self):
		return reverse('pomichnyk_core:map_detail', args=[self.slug,])

class StratImg(models.Model):
	img = models.ImageField(verbose_name='Зображення', upload_to=ImageUploadTo("cs2pedia/strategies"),)
	img_mini = models.ImageField(verbose_name='Стиснуте зображення', upload_to=ImageUploadTo("cs2pedia/strategies/mini", suffix="_mini"), null=True, blank=True)
	name = models.CharField(verbose_name="Назва", max_length=250, null=True, blank=True)
	alt_text = models.CharField(verbose_name="Альт атрибут", max_length=250, null=True, blank=True)
	comment = models.CharField(verbose_name="Підпис", max_length=250, null=True, blank=True)
	created_at = models.DateTimeField(verbose_name='Створено', auto_now_add=True, null=True)

	def __str__(self):
		return self.img.name if self.img else "No image"

	class Meta:
		verbose_name = 'Зображення'
		verbose_name_plural = 'Зображення'
		ordering = ['-created_at']

	def rename_file_field(self, field_name, suffix=""):
		file_field = getattr(self, field_name)

		if not file_field:
			return

		old_path = file_field.name
		new_path = build_renamed_image_path(old_path, self.name, suffix=suffix)

		if old_path == new_path:
			return

		storage = file_field.storage

		if storage.exists(new_path):
			# Optional but useful: avoid overwriting another file.
			base, ext = os.path.splitext(new_path)
			counter = 2

			while storage.exists(f"{base}_{counter}{ext}"):
				counter += 1

			new_path = f"{base}_{counter}{ext}"

		with storage.open(old_path, "rb") as old_file:
			storage.save(new_path, ContentFile(old_file.read()))

		storage.delete(old_path)
		file_field.name = new_path

	def save(self, *args, **kwargs):
		name_changed = False

		if self.pk:
			old = type(self).objects.filter(pk=self.pk).only("name").first()
			if old and old.name != self.name:
				name_changed = True

		super().save(*args, **kwargs)

		if self.name and name_changed:
			self.rename_file_field("img")
			self.rename_file_field("img_mini", suffix="_mini")

			super().save(update_fields=["img", "img_mini"])

class Strategy(models.Model):
	mapa = models.ForeignKey(Map, verbose_name="Мапа", on_delete=models.CASCADE, related_name="map_strategies")
	name = models.CharField(verbose_name="Назва", max_length=200)
	slug = models.SlugField(verbose_name='Слаг', unique=True)
	meta = models.CharField(verbose_name="Мета", max_length=250, blank=True, null=True)
	side = models.CharField(verbose_name="Сторона", max_length=10, choices=[("T", "T"), ("CT", "CT")])
	description = CKEditor5Field(verbose_name="Вміст", config_name='extends', blank=True)
	slide = models.ManyToManyField(StratImg, blank=True, verbose_name="Зображення")

	likes = models.IntegerField(default=0, verbose_name="Вподобання")
	is_active = models.BooleanField(verbose_name="В роботі", default=True)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Автор", on_delete=models.SET_NULL, null=True, editable=False, related_name="creator_strategies",)
	created_at = models.DateTimeField(verbose_name='Створено', auto_now_add=True, null=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Страта"
		verbose_name_plural = "Страти"
		ordering = ["mapa", "name", "-likes",]

	def get_absolute_url(self):
		return reverse('pomichnyk_core:strat_detail', args=[self.slug,])

class LineupImg(models.Model):
	img = models.ImageField(verbose_name='Зображення', upload_to=ImageUploadTo("cs2pedia/lineups"),)
	img_mini = models.ImageField(verbose_name='Стиснуте зображення', upload_to=ImageUploadTo("cs2pedia/lineups/mini", suffix="_mini"), null=True, blank=True)
	name = models.CharField(verbose_name="Назва", max_length=250, null=True, blank=True)
	alt_text = models.CharField(verbose_name="Альт атрибут", max_length=250, null=True, blank=True)
	comment = models.CharField(verbose_name="Підпис", max_length=250, null=True, blank=True)
	created_at = models.DateTimeField(verbose_name='Створено', auto_now_add=True, null=True)

	def __str__(self):
		return self.img.name if self.img else "No image"

	class Meta:
		verbose_name = 'Зображення'
		verbose_name_plural = 'Зображення'
		ordering = ['-created_at']

	def rename_file_field(self, field_name, suffix=""):
		file_field = getattr(self, field_name)

		if not file_field:
			return

		old_path = file_field.name
		new_path = build_renamed_image_path(old_path, self.name, suffix=suffix)

		if old_path == new_path:
			return

		storage = file_field.storage

		if storage.exists(new_path):
			# Optional but useful: avoid overwriting another file.
			base, ext = os.path.splitext(new_path)
			counter = 2

			while storage.exists(f"{base}_{counter}{ext}"):
				counter += 1

			new_path = f"{base}_{counter}{ext}"

		with storage.open(old_path, "rb") as old_file:
			storage.save(new_path, ContentFile(old_file.read()))

		storage.delete(old_path)
		file_field.name = new_path

	def save(self, *args, **kwargs):
		name_changed = False

		if self.pk:
			old = type(self).objects.filter(pk=self.pk).only("name").first()
			if old and old.name != self.name:
				name_changed = True

		super().save(*args, **kwargs)

		if self.name and name_changed:
			self.rename_file_field("img")
			self.rename_file_field("img_mini", suffix="_mini")

			super().save(update_fields=["img", "img_mini"])

class Lineup(models.Model):
	mapa = models.ForeignKey(Map, verbose_name="Мапа", on_delete=models.CASCADE, related_name="map_lineups")
	title = models.CharField(verbose_name="Назва", max_length=200)
	description = models.CharField(verbose_name="Опис лайнапу", max_length=200, blank=True, help_text="Наприклад: W + jumpthrow.")
	comment = models.TextField(verbose_name="Додатковий коментар", blank=True)

	class UtilityType(models.TextChoices):
		SMOKE = "smoke", "Смок"
		MOLOTOV = "molotov", "Молік"
		FLASH = "flash", "Флеш"
		HE = "he", "ХаЕ"
		DECOY = "decoy", "Декой"
	
	utility = models.CharField(verbose_name="Граната", max_length=10, choices=UtilityType.choices)
	throw_from = models.CharField(verbose_name="Звідки", max_length=100, blank=True)
	land_at = models.CharField(verbose_name="Куди", max_length=100, blank=True)

	slide = models.ManyToManyField(LineupImg, blank=True, verbose_name="Зображення")
	video_url = models.URLField(verbose_name="Відео", blank=True, help_text="Посилання на відео завантажене кудись. Потім можемо домовитись про конкретну платформу або локальне зберігання.")

	likes = models.IntegerField(default=0, verbose_name="Вподобання")
	is_published = models.BooleanField(verbose_name='Опублікувати', default=True)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Автор", on_delete=models.SET_NULL, null=True, editable=False, related_name="creator_lineups",)
	created_at = models.DateTimeField(verbose_name='Створено', auto_now_add=True, null=True)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "Лайнап"
		verbose_name_plural = "Лайнапи"
		ordering = ["mapa", "title", "-likes",]

	def get_embed_url(self):
		if "youtube.com" in self.video_url:
			return self.video_url.replace("watch?v=", "embed/")
		return self.video_url

class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="Користувач", on_delete=models.CASCADE, related_name="profile",)

	display_name = models.CharField(verbose_name="Нікнейм", max_length=100, blank=True)
	bio = models.TextField(verbose_name="Біо", blank=True)
	avatar = models.ImageField(verbose_name="Аватарка", upload_to="profiles/avatars/", blank=True, null=True)

	def __str__(self):
		return self.display_name or self.user.username