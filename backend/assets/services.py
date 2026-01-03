"""
Business logic services for asset calculations
"""
from django.db.models import Q, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Asset, Purchase, Transfer, Assignment, Expenditure


class AssetCalculationService:
    """Service class for calculating asset metrics"""
    
    @staticmethod
    def get_opening_balance(base_id, asset_type_id, start_date):
        """
        Calculate opening balance for a base and asset type at a given date.
        Opening balance = Initial inventory + Purchases before start_date + 
                         Transfers In before start_date - Transfers Out before start_date - 
                         Expenditures before start_date
        """
        # Get initial asset quantity (if exists)
        try:
            initial_asset = Asset.objects.get(base_id=base_id, asset_type_id=asset_type_id)
            initial_qty = initial_asset.quantity
        except Asset.DoesNotExist:
            initial_qty = 0
        
        # Calculate net changes before start_date
        purchases = Purchase.objects.filter(
            base_id=base_id,
            asset_type_id=asset_type_id,
            purchase_date__lt=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        transfers_in = Transfer.objects.filter(
            destination_base_id=base_id,
            asset_type_id=asset_type_id,
            transfer_date__date__lt=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        transfers_out = Transfer.objects.filter(
            source_base_id=base_id,
            asset_type_id=asset_type_id,
            transfer_date__date__lt=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        expenditures = Expenditure.objects.filter(
            base_id=base_id,
            asset_type_id=asset_type_id,
            expenditure_date__lt=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Opening balance calculation
        opening_balance = initial_qty + purchases + transfers_in - transfers_out - expenditures
        
        return max(0, opening_balance)  # Ensure non-negative
    
    @staticmethod
    def get_closing_balance(base_id, asset_type_id, end_date):
        """Calculate closing balance at end_date"""
        return AssetCalculationService.get_opening_balance(
            base_id, asset_type_id, end_date + timedelta(days=1)
        )
    
    @staticmethod
    def get_net_movement(base_id, asset_type_id, start_date, end_date):
        """
        Calculate net movement in date range.
        Net Movement = Purchases + Transfers In - Transfers Out
        """
        purchases = Purchase.objects.filter(
            base_id=base_id,
            asset_type_id=asset_type_id,
            purchase_date__gte=start_date,
            purchase_date__lte=end_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        transfers_in = Transfer.objects.filter(
            destination_base_id=base_id,
            asset_type_id=asset_type_id,
            transfer_date__date__gte=start_date,
            transfer_date__date__lte=end_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        transfers_out = Transfer.objects.filter(
            source_base_id=base_id,
            asset_type_id=asset_type_id,
            transfer_date__date__gte=start_date,
            transfer_date__date__lte=end_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return {
            'purchases': float(purchases),
            'transfers_in': float(transfers_in),
            'transfers_out': float(transfers_out),
            'net_movement': float(purchases + transfers_in - transfers_out)
        }
    
    @staticmethod
    def get_assigned_assets(base_id, asset_type_id, start_date, end_date):
        """Get total assigned assets in date range"""
        assigned = Assignment.objects.filter(
            base_id=base_id,
            asset_type_id=asset_type_id,
            assignment_date__gte=start_date,
            assignment_date__lte=end_date,
            status='active'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return float(assigned)
    
    @staticmethod
    def get_expended_assets(base_id, asset_type_id, start_date, end_date):
        """Get total expended assets in date range"""
        expended = Expenditure.objects.filter(
            base_id=base_id,
            asset_type_id=asset_type_id,
            expenditure_date__gte=start_date,
            expenditure_date__lte=end_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return float(expended)
    
    @staticmethod
    def get_dashboard_data(base_id=None, asset_type_id=None, start_date=None, end_date=None):
        """
        Get comprehensive dashboard data with filters.
        Returns aggregated data for all bases/asset types if filters not provided.
        """
        if not start_date:
            start_date = timezone.now().date() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
        
        # Build query filters
        base_filter = Q()
        asset_filter = Q()
        
        if base_id:
            base_filter = Q(base_id=base_id) | Q(source_base_id=base_id) | Q(destination_base_id=base_id)
        
        if asset_type_id:
            asset_filter = Q(asset_type_id=asset_type_id)
        
        # Get all relevant bases and asset types
        from .models import Base, AssetType
        
        bases = Base.objects.all()
        asset_types = AssetType.objects.all()
        
        if base_id:
            bases = bases.filter(id=base_id)
        if asset_type_id:
            asset_types = asset_types.filter(id=asset_type_id)
        
        dashboard_data = []
        
        for base in bases:
            for asset_type in asset_types:
                opening = AssetCalculationService.get_opening_balance(
                    base.id, asset_type.id, start_date
                )
                closing = AssetCalculationService.get_closing_balance(
                    base.id, asset_type.id, end_date
                )
                net_movement_data = AssetCalculationService.get_net_movement(
                    base.id, asset_type.id, start_date, end_date
                )
                assigned = AssetCalculationService.get_assigned_assets(
                    base.id, asset_type.id, start_date, end_date
                )
                expended = AssetCalculationService.get_expended_assets(
                    base.id, asset_type.id, start_date, end_date
                )
                
                dashboard_data.append({
                    'base_id': base.id,
                    'base_name': base.name,
                    'asset_type_id': asset_type.id,
                    'asset_type_name': asset_type.name,
                    'asset_type_category': asset_type.category,
                    'opening_balance': opening,
                    'closing_balance': closing,
                    'net_movement': net_movement_data['net_movement'],
                    'net_movement_details': {
                        'purchases': net_movement_data['purchases'],
                        'transfers_in': net_movement_data['transfers_in'],
                        'transfers_out': net_movement_data['transfers_out'],
                    },
                    'assigned_assets': assigned,
                    'expended_assets': expended,
                })
        
        return dashboard_data


