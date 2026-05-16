from django.urls import path
from nudge.views import NudgeView

urlpatterns = [
    path('', NudgeView.as_view(), name='nudge'),
]