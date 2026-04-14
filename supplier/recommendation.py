import datetime

from django.db.models import Avg, Sum
from .models import Supplier, SupplierStat


try:
    import pandas as pd
    from sklearn.neighbors import NearestNeighbors
    from sklearn.preprocessing import StandardScaler
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False


def _build_supplier_feature_dataframe(days=None):
    queryset = SupplierStat.objects.select_related('supplier')
    if days is not None:
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        queryset = queryset.filter(date__gte=cutoff)

    aggregated = queryset.values(
        'supplier_id',
        'supplier__name',
        'supplier__approval_status'
    ).annotate(
        total_spend=Sum('total_spend'),
        orders_count=Sum('orders_count'),
        avg_order=Avg('avg_order')
    )

    return list(aggregated)


def _recommended_by_spend(top=5, days=None, supplier_id=None):
    aggregated = _build_supplier_feature_dataframe(days=days)
    approved = [item for item in aggregated if item['supplier__approval_status'] == 'approved']
    approved.sort(key=lambda x: x['total_spend'] or 0, reverse=True)
    if supplier_id is not None:
        approved = [item for item in approved if item['supplier_id'] != supplier_id]
    supplier_ids = [item['supplier_id'] for item in approved[:top]]
    return list(Supplier.objects.filter(id__in=supplier_ids))


def recommend_suppliers(top=5, days=None, supplier_id=None):
    if not HAS_ML_LIBS:
        return _recommended_by_spend(top=top, days=days, supplier_id=supplier_id)

    aggregated = _build_supplier_feature_dataframe(days=days)
    approved = [item for item in aggregated if item['supplier__approval_status'] == 'approved']
    if not approved:
        return Supplier.objects.none()

    df = pd.DataFrame(approved).fillna({'total_spend': 0, 'orders_count': 0, 'avg_order': 0})
    features = df[['total_spend', 'orders_count', 'avg_order']]

    if supplier_id is None or supplier_id not in df['supplier_id'].values:
        top_supplier_ids = df.sort_values(by='total_spend', ascending=False)['supplier_id'].head(top).tolist()
        return list(Supplier.objects.filter(id__in=top_supplier_ids))

    if len(df) <= 1:
        supplier_ids = df.loc[df['supplier_id'] != supplier_id, 'supplier_id'].head(top).tolist()
        return list(Supplier.objects.filter(id__in=supplier_ids))

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    neigh = NearestNeighbors(metric='cosine', algorithm='auto')
    neigh.fit(scaled)

    supplier_index = df.index[df['supplier_id'] == supplier_id].tolist()[0]
    n_neighbors = min(len(df), top + 1)
    distances, indices = neigh.kneighbors([scaled[supplier_index]], n_neighbors=n_neighbors)

    recommended_ids = [df.iloc[idx]['supplier_id'] for idx in indices[0] if df.iloc[idx]['supplier_id'] != supplier_id]
    return list(Supplier.objects.filter(id__in=recommended_ids[:top]))
