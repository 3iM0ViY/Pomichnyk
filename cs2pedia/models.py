from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.

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
	img = models.ImageField(verbose_name='Зображення', upload_to="cs2pedia/strategies")
	img_mini = models.ImageField(verbose_name='Стиснуте зображення', upload_to="cs2pedia/strategies/mini", null=True, blank=True)
	alt_text = models.CharField(verbose_name="Підпис", max_length=250, null=True, blank=True)
	created_at = models.DateTimeField(verbose_name='Створено', auto_now_add=True, null=True)

	def __str__(self):
		return self.img.name if self.img else "No image"

	class Meta:
		verbose_name = 'Зображення'
		verbose_name_plural = 'Зображення'
		ordering = ['-created_at']

class Strategy(models.Model):
	mapa = models.ForeignKey(Map, verbose_name="Мапа", on_delete=models.CASCADE, related_name="map_strategies")
	name = models.CharField(verbose_name="Назва", max_length=200)
	side = models.CharField(verbose_name="Сторона", max_length=10, choices=[("T", "T"), ("CT", "CT")])
	description = models.TextField(verbose_name="Вміст", blank=True)
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

class LineupImg(models.Model):
	img = models.ImageField(verbose_name='Зображення', upload_to="cs2pedia/lineups")
	img_mini = models.ImageField(verbose_name='Стиснуте зображення', upload_to="cs2pedia/lineups/mini", null=True, blank=True)
	alt_text = models.CharField(verbose_name="Підпис", max_length=250, null=True, blank=True)
	created_at = models.DateTimeField(verbose_name='Створено', auto_now_add=True, null=True)

	def __str__(self):
		return self.img.name if self.img else "No image"

	class Meta:
		verbose_name = 'Зображення'
		verbose_name_plural = 'Зображення'
		ordering = ['-created_at']

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