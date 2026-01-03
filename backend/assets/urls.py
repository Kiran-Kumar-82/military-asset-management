"""
URLs for assets app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BaseViewSet, AssetTypeViewSet, AssetViewSet,
    PurchaseViewSet, TransferViewSet, AssignmentViewSet,
    ExpenditureViewSet, DashboardViewSet
)

router = DefaultRouter()
router.register(r'bases', BaseViewSet, basename='base')
router.register(r'asset-types', AssetTypeViewSet, basename='asset-type')
router.register(r'inventory', AssetViewSet, basename='asset')
router.register(r'purchases', PurchaseViewSet, basename='purchase')
router.register(r'transfers', TransferViewSet, basename='transfer')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'expenditures', ExpenditureViewSet, basename='expenditure')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]


