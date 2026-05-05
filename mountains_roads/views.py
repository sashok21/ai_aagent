from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse

from .models import MountainRoute, RouteReview, UserProfile
from .forms import RouteReviewForm, UserRegistrationForm, UserProfileForm


class HomePageView(TemplateView):
    template_name = 'mountains_roads/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_routes'] = MountainRoute.objects.all().order_by('-rating')[:3]
        context['total_routes'] = MountainRoute.objects.count()
        context['total_reviews'] = RouteReview.objects.count()
        return context


class RoutesListView(ListView):
    model = MountainRoute
    template_name = 'mountains_roads/routes_list.html'
    context_object_name = 'routes'
    paginate_by = 12

    def get_queryset(self):
        queryset = MountainRoute.objects.all()

        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        region = self.request.GET.get('region')
        if region:
            queryset = queryset.filter(region=region)

        min_height = self.request.GET.get('min_height')
        max_height = self.request.GET.get('max_height')
        if min_height:
            queryset = queryset.filter(height__gte=int(min_height))
        if max_height:
            queryset = queryset.filter(height__lte=int(max_height))

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        sort = self.request.GET.get('sort', '-rating')
        queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = MountainRoute.objects.values_list('region', flat=True).distinct()
        context['difficulties'] = MountainRoute.DIFFICULTY_CHOICES
        return context


class RouteDetailView(DetailView):
    model = MountainRoute
    template_name = 'mountains_roads/route_detail.html'
    context_object_name = 'route'
    slug_field = 'id'
    slug_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        context['average_rating'] = self.object.get_average_rating()

        if self.request.user.is_authenticated:
            user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            context['is_favorite'] = self.object in user_profile.favorite_routes.all()
            context['is_completed'] = self.object in user_profile.completed_routes.all()

        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = RouteReview
    form_class = RouteReviewForm
    template_name = 'mountains_roads/review_form.html'
    login_url = 'login'

    def form_valid(self, form):
        route_id = self.kwargs['route_id']
        route = get_object_or_404(MountainRoute, id=route_id)

        existing_review = RouteReview.objects.filter(route=route, user=self.request.user)
        if existing_review.exists():
            messages.error(self.request, "Ви вже залишили відгук до цього маршруту")
            return redirect('route-detail', pk=route_id)

        form.instance.route = route
        form.instance.user = self.request.user
        response = super().form_valid(form)

        route.rating = route.get_average_rating()
        route.save()

        messages.success(self.request, "Дякуємо за ваш відгук!")
        return response

    def get_success_url(self):
        return reverse_lazy('route-detail', kwargs={'pk': self.kwargs['route_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_id = self.kwargs['route_id']
        context['form'].instance.route = get_object_or_404(MountainRoute, id=route_id)
        return context


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = RouteReview
    form_class = RouteReviewForm
    template_name = 'mountains_roads/review_form.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def form_valid(self, form):
        response = super().form_valid(form)
        route = self.object.route
        route.rating = route.get_average_rating()
        route.save()
        messages.success(self.request, "Відгук успішно оновлено!")
        return response

    def get_success_url(self):
        return reverse_lazy('route-detail', kwargs={'pk': self.object.route.id})


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = RouteReview
    template_name = 'mountains_roads/review_confirm_delete.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def delete(self, request, *args, **kwargs):
        route = self.get_object().route
        response = super().delete(request, *args, **kwargs)
        route.rating = route.get_average_rating()
        route.save()
        messages.success(request, "Відгук успішно видалено")
        return response

    def get_success_url(self):
        return reverse_lazy('route-detail', kwargs={'pk': self.object.route.id})


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'mountains_roads/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        UserProfile.objects.get_or_create(user=self.object)
        messages.success(self.request, "Реєстрація успішна! Тепер ви можете увійти.")
        return response


class UserProfileView(DetailView):
    model = User
    template_name = 'mountains_roads/user_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        context['completed_routes'] = user_profile.completed_routes.all()
        context['favorite_routes'] = user_profile.favorite_routes.all()
        context['user_reviews'] = RouteReview.objects.filter(user=user)
        context['is_own_profile'] = self.request.user == user
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'mountains_roads/profile_edit.html'

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Профіль успішно оновлено!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user-profile', kwargs={'username': self.request.user.username})


@login_required
def toggle_favorite(request, route_id):
    route = get_object_or_404(MountainRoute, id=route_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if route in user_profile.favorite_routes.all():
        user_profile.favorite_routes.remove(route)
        is_favorite = False
        message = "Маршрут видалено з улюблених"
    else:
        user_profile.favorite_routes.add(route)
        is_favorite = True
        message = "Маршрут додано в улюблені"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite, 'message': message})

    messages.success(request, message)
    return redirect('route-detail', pk=route_id)


@login_required
def toggle_completed(request, route_id):
    route = get_object_or_404(MountainRoute, id=route_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if route in user_profile.completed_routes.all():
        user_profile.completed_routes.remove(route)
        is_completed = False
        message = "Маршрут позначено як не пройдено"
    else:
        user_profile.completed_routes.add(route)
        is_completed = True
        message = "Вітаємо! Маршрут позначено як пройдено"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_completed': is_completed, 'message': message})

    messages.success(request, message)
    return redirect('route-detail', pk=route_id)