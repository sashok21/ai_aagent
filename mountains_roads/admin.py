from django.contrib import admin
from .models import MountainRoute, RouteReview, UserProfile


@admin.register(MountainRoute)
class MountainRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'height', 'difficulty', 'rating', 'created_at']
    list_filter = ['difficulty', 'region', 'created_at']
    search_fields = ['name', 'description', 'region']
    ordering = ['-rating', '-created_at']
    list_per_page = 20


@admin.register(RouteReview)
class RouteReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'route', 'rating', 'title', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['title', 'text', 'user__username', 'route__name']
    ordering = ['-created_at']
    list_per_page = 20


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'get_completed_count', 'get_favorites_count']
    search_fields = ['user__username', 'user__email', 'bio']
    filter_horizontal = ['completed_routes', 'favorite_routes']
    ordering = ['-created_at']

    def get_completed_count(self, obj):
        return obj.completed_routes.count()

    get_completed_count.short_description = 'Пройдено маршрутів'

    def get_favorites_count(self, obj):
        return obj.favorite_routes.count()

    get_favorites_count.short_description = 'Улюблених маршрутів'