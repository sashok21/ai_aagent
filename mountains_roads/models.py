from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class MountainRoute(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легка'),
        ('medium', 'Середня'),
        ('hard', 'Важка'),
    ]

    name = models.CharField(max_length=200, verbose_name="Назва маршруту")
    description = models.TextField(verbose_name="Опис")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name="Складність")
    height = models.IntegerField(verbose_name="Висота (м)", validators=[MinValueValidator(0)])
    duration_hours = models.FloatField(verbose_name="Тривалість (годин)", validators=[MinValueValidator(0.5)])
    distance_km = models.FloatField(verbose_name="Відстань (км)", validators=[MinValueValidator(0)])
    # Додано null=True, blank=True для безпеки
    image = models.ImageField(upload_to='routes/', null=True, blank=True, verbose_name="Основне фото")
    map_coordinates = models.CharField(max_length=100, verbose_name="Координати (lat,lng)")
    gpx_file = models.FileField(upload_to='gpx/', null=True, blank=True, verbose_name="GPX файл маршруту")
    region = models.CharField(max_length=100, verbose_name="Регіон")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    class Meta:
        verbose_name = "Гірський маршрут"
        verbose_name_plural = "Гірські маршрути"
        ordering = ['-rating']

    def __str__(self):
        return self.name

    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0


class RouteReview(models.Model):
    route = models.ForeignKey(MountainRoute, on_delete=models.CASCADE, related_name='reviews', verbose_name="Маршрут")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Оцінка")
    title = models.CharField(max_length=200, verbose_name="Заголовок відгуку")
    text = models.TextField(verbose_name="Текст відгуку")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    helpful_count = models.IntegerField(default=0, verbose_name="Кількість корисних")

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ['-created_at']
        unique_together = ['route', 'user']

    def __str__(self):
        return f"Відгук від {self.user} до {self.route}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Користувач")
    bio = models.TextField(blank=True, verbose_name="Біографія")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    completed_routes = models.ManyToManyField(MountainRoute, blank=True, related_name='completed_by', verbose_name="Пройдені маршрути")
    favorite_routes = models.ManyToManyField(MountainRoute, blank=True, related_name='favorited_by', verbose_name="Улюблені маршрути")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"

    def __str__(self):
        return f"Профіль {self.user.username}"

    def routes_count(self):
        return self.completed_routes.count()