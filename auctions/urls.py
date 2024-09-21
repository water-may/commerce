from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:auction_id>", views.listing, name="listing"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close_list/<int:auction_id>", views.close_list, name="close_list"),
    path("comment/<int:auction_id>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path(f"category/<str:cat>", views.category, name="category")
]
