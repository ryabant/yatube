from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug>/", views.group_posts, name="group"),
    path("new/", views.new_post, name="new_post"),
    path("<username>/", views.profile, name="profile"),
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    path("<username>/<int:post_id>/edit/",
         views.post_edit, name="post_edit"),
]
