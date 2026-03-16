from django.urls import path
from .views import POListView

urlpatterns = [
    path('po/list/', POListView.as_view(), name='datatable-po-list'),
]
