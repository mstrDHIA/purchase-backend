from django.urls import path
from .views import POTotalsView, PORejectionRateView, total_price_dinar_view

urlpatterns = [
    path('po/totals/', POTotalsView.as_view(), name='po-totals'),
    path('po/rejection-rate/', PORejectionRateView.as_view(), name='po-rejection-rate'),
    path('po/total-price-dinar/', total_price_dinar_view, name='po-total-price-dinar'),
]
