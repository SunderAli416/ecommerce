from django.contrib import admin
from django.urls import path, include
from . import views
app_name='api'
urlpatterns = [
   path('',views.overview, name="overview"),
   path('verify/',views.verify, name="verify",)
]