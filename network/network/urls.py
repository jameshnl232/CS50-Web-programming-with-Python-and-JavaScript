
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("users/<str:username>", views.user_page, name="user_page"),
    path("following", views.following, name="following"),

    # API routes
    path("new-post", views.new_post, name="new_post"),
    path("posts/<str:id>", views.get_post, name="get_post"),
    path('toggle_like/<int:post_id>/', views.toggle_like, name='toggle_like')
]
