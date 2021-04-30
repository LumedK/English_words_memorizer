from django.urls import path
from . import views

urlpatterns = [
    path('', views.DebugHomeView.as_view()),
    path('list/<int:pk>', views.MemorizingListView.as_view(), name='memorizing_list'),
    path('word/<int:pk>', views.WordView.as_view(), name='word'),
]
