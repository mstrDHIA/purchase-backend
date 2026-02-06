from django.urls import path
from .views import POTotalsView, PORejectionRateView

urlpatterns = [
    path('po/totals/', POTotalsView.as_view(), name='po-totals'),
    path('po/rejection-rate/', PORejectionRateView.as_view(), name='po-rejection-rate'),
]
