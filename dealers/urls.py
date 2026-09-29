from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), path("inventory/", views.inventory, name="inventory"),
    path("vehicles/<slug:slug>/", views.vehicle_detail, name="vehicle_detail"),
    path("dashboard/", views.dashboard, name="dashboard"), path("dashboard/inventory/", views.dashboard_inventory, name="dashboard_inventory"),
    path("dashboard/inventory/new/", views.vehicle_create, name="vehicle_create"), path("dashboard/inventory/<uuid:pk>/", views.vehicle_edit, name="vehicle_edit"),
    path("dashboard/images/<int:pk>/delete/", views.image_delete, name="image_delete"), path("dashboard/images/<int:pk>/move/", views.image_move, name="image_move"),
    path("dashboard/requests/", views.requests_list, name="requests_list"), path("dashboard/requests/<int:pk>/status/", views.request_status, name="request_status"),
    path("dashboard/settings/", views.dealer_settings, name="dealer_settings"), path("sitemap.xml", views.sitemap, name="sitemap"), path("robots.txt", views.robots, name="robots"), path("health/", views.health, name="health"),
]
