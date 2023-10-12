from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/create", views.create_listing, name="create_listing"),
    path("listings/<int:listing_id>", views.display_listing, name="display_listing"),
    path("listings/<int:listing_id>/close", views.close_listing, name="close_listing"),
    path("watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category", views.category, name="category"),
    path("category/<str:category>", views.display_listing_category, name="display_listing_category")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
