from django.urls import path

from realtime.api.views import AnalyticsView

urlpatterns = [
    path('', AnalyticsView.as_view(), name='analytics')
]
