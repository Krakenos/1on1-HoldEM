from django.urls import path, include
from rest_framework import routers

from game.views import Games

router = routers.DefaultRouter()
router.register(r'game', Games)
urlpatterns = [
    path('', include(router.urls))
]