"""
Views for Asset Management System
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Base, AssetType, Asset, Purchase, Transfer, Assignment, Expenditure
from .serializers import (
    BaseSerializer, AssetTypeSerializer, AssetSerializer,
    PurchaseSerializer, TransferSerializer, AssignmentSerializer, ExpenditureSerializer
)
from .services import AssetCalculationService
from accounts.permissions import (
    IsAdmin, IsBaseCommander, IsLogisticsOfficer, IsAdminOrLogisticsOfficer, BaseAccessPermission
)


class BaseViewSet(viewsets.ModelViewSet):
    """ViewSet for Base management"""
    queryset = Base.objects.all()
    serializer_class = BaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin():
            return Base.objects.all()
        elif user.is_base_commander() and user.assigned_base:
            return Base.objects.filter(id=user.assigned_base.id)
        return Base.objects.none()


class AssetTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for AssetType management"""
    queryset = AssetType.objects.all()
    serializer_class = AssetTypeSerializer
    permission_classes = [IsAuthenticated]


class AssetViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing Asset inventory"""
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Asset.objects.all()
        
        # Base Commanders can only see their base
        if user.is_base_commander() and user.assigned_base:
            queryset = queryset.filter(base=user.assigned_base)
        
        # Filter by base and asset_type if provided
        base_id = self.request.query_params.get('base_id')
        asset_type_id = self.request.query_params.get('asset_type_id')
        
        if base_id:
            queryset = queryset.filter(base_id=base_id)
        if asset_type_id:
            queryset = queryset.filter(asset_type_id=asset_type_id)
        
        return queryset


class PurchaseViewSet(viewsets.ModelViewSet):
    """ViewSet for Purchase management"""
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAdminOrLogisticsOfficer]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Purchase.objects.all()
        
        # Base Commanders can only see their base's purchases
        if user.is_base_commander() and user.assigned_base:
            queryset = queryset.filter(base=user.assigned_base)
        
        # Filter by base, asset_type, date range
        base_id = self.request.query_params.get('base_id')
        asset_type_id = self.request.query_params.get('asset_type_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if base_id:
            queryset = queryset.filter(base_id=base_id)
        if asset_type_id:
            queryset = queryset.filter(asset_type_id=asset_type_id)
        if start_date:
            queryset = queryset.filter(purchase_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(purchase_date__lte=end_date)
        
        return queryset.order_by('-purchase_date', '-created_at')
    
    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except ValueError as e:
            # Handle insufficient inventory errors
            if 'Insufficient inventory' in str(e):
                raise ValidationError({'detail': str(e)})
            raise


class TransferViewSet(viewsets.ModelViewSet):
    """ViewSet for Transfer management"""
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [IsAdminOrLogisticsOfficer]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Transfer.objects.all()
        
        # Base Commanders can only see transfers involving their base
        if user.is_base_commander() and user.assigned_base:
            queryset = queryset.filter(
                Q(source_base=user.assigned_base) | Q(destination_base=user.assigned_base)
            )
        
        # Filter by base, asset_type, date range
        base_id = self.request.query_params.get('base_id')
        asset_type_id = self.request.query_params.get('asset_type_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if base_id:
            queryset = queryset.filter(
                Q(source_base_id=base_id) | Q(destination_base_id=base_id)
            )
        if asset_type_id:
            queryset = queryset.filter(asset_type_id=asset_type_id)
        if start_date:
            queryset = queryset.filter(transfer_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transfer_date__date__lte=end_date)
        
        return queryset.order_by('-transfer_date', '-created_at')
    
    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except ValueError as e:
            # Handle insufficient inventory errors
            if 'Insufficient inventory' in str(e):
                raise ValidationError({'detail': str(e)})
            raise


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Assignment management"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Assignment.objects.all()
        
        # Base Commanders can only see their base's assignments
        if user.is_base_commander() and user.assigned_base:
            queryset = queryset.filter(base=user.assigned_base)
        
        # Filter by base, asset_type, date range, status
        base_id = self.request.query_params.get('base_id')
        asset_type_id = self.request.query_params.get('asset_type_id')
        status_filter = self.request.query_params.get('status')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if base_id:
            queryset = queryset.filter(base_id=base_id)
        if asset_type_id:
            queryset = queryset.filter(asset_type_id=asset_type_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if start_date:
            queryset = queryset.filter(assignment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(assignment_date__lte=end_date)
        
        return queryset.order_by('-assignment_date', '-created_at')
    
    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except ValueError as e:
            # Handle insufficient inventory errors
            if 'Insufficient inventory' in str(e):
                raise ValidationError({'detail': str(e)})
            raise


class ExpenditureViewSet(viewsets.ModelViewSet):
    """ViewSet for Expenditure management"""
    queryset = Expenditure.objects.all()
    serializer_class = ExpenditureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Expenditure.objects.all()
        
        # Base Commanders can only see their base's expenditures
        if user.is_base_commander() and user.assigned_base:
            queryset = queryset.filter(base=user.assigned_base)
        
        # Filter by base, asset_type, date range
        base_id = self.request.query_params.get('base_id')
        asset_type_id = self.request.query_params.get('asset_type_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if base_id:
            queryset = queryset.filter(base_id=base_id)
        if asset_type_id:
            queryset = queryset.filter(asset_type_id=asset_type_id)
        if start_date:
            queryset = queryset.filter(expenditure_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expenditure_date__lte=end_date)
        
        return queryset.order_by('-expenditure_date', '-created_at')
    
    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except ValueError as e:
            # Handle insufficient inventory errors
            if 'Insufficient inventory' in str(e):
                raise ValidationError({'detail': str(e)})
            raise


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for Dashboard data"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def data(self, request):
        """Get dashboard data with filters"""
        base_id = request.query_params.get('base_id')
        asset_type_id = request.query_params.get('asset_type_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Parse dates
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date() - timedelta(days=30)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        # Apply base filter for Base Commanders
        user = request.user
        if user.is_base_commander() and user.assigned_base:
            base_id = user.assigned_base.id
        
        dashboard_data = AssetCalculationService.get_dashboard_data(
            base_id=base_id,
            asset_type_id=asset_type_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response(dashboard_data)

