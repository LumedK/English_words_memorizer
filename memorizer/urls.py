from django.urls import path
from . import views

urlpatterns = [
    path('', views.DebugHomeView.as_view()),
    path('list/<int:pk>', views.MemorizingListView.as_view(), name='memorizing_list'),
    path('word/<int:pk>', views.WordView.as_view(), name='word'),
    path('run_list/<int:list_pk>', views.RunListView.as_view(), name='run_list'),
    path('delete_context/', views.DeleteContextView.as_view(), name='delete_context')
]
