from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/New_Page", views.new_page, name="new_page"),
    path("wiki/edit/<str:title>", views.edit, name="edit"),
    path("wiki/<str:entry>", views.entry, name="entry"),
    path("search", views.search, name="search"),
    path("random", views.random_entry, name="random")


]
