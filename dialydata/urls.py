
from django.urls import path
from .views import addData,getData
urlpatterns = [
    path('add/', addData,name='addData'),
    path('get/<str:date>/', getData,name='getData'),
]
