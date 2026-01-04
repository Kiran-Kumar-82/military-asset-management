from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
import json

from assets.models import (
    Asset, Base, EquipmentType, Personnel, Purchase, Transfer, 
    Assignment, Expenditure, TransactionLog, TransferLog
)
from assets.forms import (
    PurchaseForm, TransferForm, AssignmentForm, ExpenditureForm, 
    DashboardFilterForm, ReturnAssignmentForm
)


def get_user_base(user):
    """Get the base associated with the current user"""
    try:
        if user.personnel:
            return user.personnel.base
    except:
        pass
    
    # Check if user is a base commander
    try:
        if user.commanded_base:
            return user.commanded_base
    except:
        pass
    
    return None


def user_can_access_base(user, base):
    """Check if user can access a specific base"""
    if user.is_superuser:
        return True
    
    # Logistics officers can access all bases
    if user.groups.filter(name='Logistics Officer').exists():
        return True
    
    user_base = get_user_base(user)
    return user_base == base if user_base else False


def filter_assets_for_user(user, queryset):
    """Filter assets based on user permissions"""
    if user.is_superuser:
        return queryset
    
    if user.groups.filter(name='Logistics Officer').exists():
        return queryset
    
    user_base = get_user_base(user)
    if user_base:
        return queryset.filter(base=user_base)
    
    return queryset.none()


@login_required
def dashboard(request):
    """Dashboard with key metrics and filters"""
    user_base = get_user_base(request.user)
    
    # Get filter form
    filter_form = DashboardFilterForm(request.GET or None)
    
    # Get assets
    assets = Asset.objects.all()
    if not request.user.is_superuser and not request.user.groups.filter(name='Logistics Officer').exists():
        if user_base:
            assets = assets.filter(base=user_base)
        else:
            assets = assets.none()
    
    # Apply filters
    if filter_form.is_valid():
        base = filter_form.cleaned_data.get('base')
        equipment_type = filter_form.cleaned_data.get('equipment_type')
        
        if base:
            assets = assets.filter(base=base)
        if equipment_type:
            assets = assets.filter(equipment_type=equipment_type)
    
    # Calculate metrics
    total_opening_balance = assets.aggregate(total=Sum('opening_balance'))['total'] or 0
    total_closing_balance = assets.aggregate(total=Sum('closing_balance'))['total'] or 0
    total_assigned = assets.aggregate(total=Sum('assigned_count'))['total'] or 0
    total_expended = assets.aggregate(total=Sum('expended_count'))['total'] or 0
    
    # Get recent transactions
    recent_transactions = TransactionLog.objects.select_related('asset', 'created_by').all()[:10]
    
    context = {
        'assets': assets,
        'filter_form': filter_form,
        'total_opening_balance': total_opening_balance,
        'total_closing_balance': total_closing_balance,
        'total_assigned': total_assigned,
        'total_expended': total_expended,
        'recent_transactions': recent_transactions,
        'user_base': user_base,
    }
    
    return render(request, 'assets/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def purchases(request):
    """Purchase management"""
    user_base = get_user_base(request.user)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            
            # Check permissions
            if not request.user.is_superuser and not request.user.groups.filter(name='Logistics Officer').exists():
                if user_base and purchase.asset.base != user_base:
                    return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            purchase.save()
            return redirect('purchases')
    else:
        form = PurchaseForm()
    
    # Get purchases
    purchases_list = Purchase.objects.select_related('asset', 'created_by', 'approved_by').all()
    
    if not request.user.is_superuser and not request.user.groups.filter(name='Logistics Officer').exists():
        if user_base:
            purchases_list = purchases_list.filter(asset__base=user_base)
        else:
            purchases_list = purchases_list.none()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        purchases_list = purchases_list.filter(status=status_filter)
    
    context = {
        'form': form,
        'purchases': purchases_list,
        'user_base': user_base,
    }
    
    return render(request, 'assets/purchases.html', context)


@login_required
@require_http_methods(["POST"])
def approve_purchase(request, purchase_id):
    """Approve a purchase"""
    if not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    purchase = get_object_or_404(Purchase, id=purchase_id)
    purchase.approve(request.user)
    
    return JsonResponse({'status': 'success', 'message': 'Purchase approved'})


@login_required
@require_http_methods(["GET", "POST"])
def transfers(request):
    """Transfer management"""
    user_base = get_user_base(request.user)
    
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.initiated_by = request.user
            
            # Check permissions - allow Admin, Logistics Officer, and Base Commanders
            if not request.user.is_superuser and not request.user.groups.filter(name='Logistics Officer').exists():
                # Base Commanders can only transfer FROM their base
                if not request.user.groups.filter(name='Base Commander').exists():
                    return JsonResponse({'error': 'Unauthorized'}, status=403)
                if user_base and transfer.from_base != user_base:
                    return JsonResponse({'error': 'Can only transfer from your base'}, status=403)
            
            transfer.save()
            
            # Create transfer logs for both bases
            try:
                from_asset = Asset.objects.get(equipment_type=transfer.equipment_type, base=transfer.from_base)
                to_asset = Asset.objects.get(equipment_type=transfer.equipment_type, base=transfer.to_base)
                
                TransferLog.objects.create(
                    asset=from_asset,
                    transfer=transfer,
                    transfer_type='OUT',
                    quantity=transfer.quantity
                )
                
                TransferLog.objects.create(
                    asset=to_asset,
                    transfer=transfer,
                    transfer_type='IN',
                    quantity=transfer.quantity
                )
            except Asset.DoesNotExist:
                pass
            
            return redirect('transfers')
    else:
        form = TransferForm()
    
    # Get transfers
    transfers_list = Transfer.objects.select_related('equipment_type', 'from_base', 'to_base').all()
    
    if not request.user.is_superuser and not request.user.groups.filter(name='Logistics Officer').exists():
        if user_base:
            transfers_list = transfers_list.filter(
                Q(from_base=user_base) | Q(to_base=user_base)
            )
        else:
            transfers_list = transfers_list.none()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        transfers_list = transfers_list.filter(status=status_filter)
    
    context = {
        'form': form,
        'transfers': transfers_list,
        'user_base': user_base,
    }
    
    return render(request, 'assets/transfers.html', context)


@login_required
@require_http_methods(["POST"])


@login_required
@require_http_methods(["POST"])
def approve_transfer(request, transfer_id):
    """Approve/Initiate a transfer from PENDING to IN_TRANSIT"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    transfer = get_object_or_404(Transfer, id=transfer_id)
    
    if transfer.status == 'PENDING':
        transfer.status = 'IN_TRANSIT'
        transfer.save()
        return JsonResponse({'status': 'success', 'message': 'Transfer initiated'})
    
    return JsonResponse({'error': 'Transfer cannot be approved'}, status=400)


@login_required
@require_http_methods(["POST"])
def complete_transfer(request, transfer_id):
    """Complete a transfer"""
    if not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    transfer = get_object_or_404(Transfer, id=transfer_id)
    transfer.complete_transfer(request.user)
    
    return JsonResponse({'status': 'success', 'message': 'Transfer completed'})


@login_required
@require_http_methods(["GET", "POST"])
def assignments(request):
    """Assignment management"""
    user_base = get_user_base(request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.assigned_by = request.user
            
            # Check permissions
            if not request.user.is_superuser:
                if user_base and assignment.asset.base != user_base:
                    return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            assignment.save()
            return redirect('assignments')
    else:
        form = AssignmentForm()
    
    # Get assignments
    assignments_list = Assignment.objects.select_related('asset', 'personnel', 'assigned_by').all()
    
    if not request.user.is_superuser:
        if user_base:
            assignments_list = assignments_list.filter(asset__base=user_base)
        else:
            assignments_list = assignments_list.none()
    
    context = {
        'form': form,
        'assignments': assignments_list,
        'user_base': user_base,
    }
    
    return render(request, 'assets/assignments.html', context)


@login_required
@require_http_methods(["POST"])
def return_assignment(request, assignment_id):
    """Return an assignment"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if not request.user.is_superuser and assignment.asset.base != get_user_base(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    assignment.return_asset()
    return JsonResponse({'status': 'success', 'message': 'Assignment returned'})


@login_required
@require_http_methods(["GET", "POST"])
def expenditures(request):
    """Expenditure management"""
    user_base = get_user_base(request.user)
    
    if request.method == 'POST':
        form = ExpenditureForm(request.POST)
        if form.is_valid():
            expenditure = form.save(commit=False)
            expenditure.recorded_by = request.user
            
            # Check permissions
            if not request.user.is_superuser:
                if user_base and expenditure.asset.base != user_base:
                    return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            expenditure.save()
            return redirect('expenditures')
    else:
        form = ExpenditureForm()
    
    # Get expenditures
    expenditures_list = Expenditure.objects.select_related('asset', 'recorded_by').all()
    
    if not request.user.is_superuser:
        if user_base:
            expenditures_list = expenditures_list.filter(asset__base=user_base)
        else:
            expenditures_list = expenditures_list.none()
    
    context = {
        'form': form,
        'expenditures': expenditures_list,
        'user_base': user_base,
    }
    
    return render(request, 'assets/expenditures.html', context)


@login_required
def asset_detail(request, asset_id):
    """Asset detail view with transaction history"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    # Check permissions
    if not request.user.is_superuser and not request.user.groups.filter(name='Logistics Officer').exists():
        if get_user_base(request.user) != asset.base:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get transaction history
    transactions = TransactionLog.objects.filter(asset=asset).select_related('created_by')
    
    # Calculate net movement breakdown
    purchases_total = asset.purchases.filter(status='APPROVED').aggregate(total=Sum('quantity'))['total'] or 0
    transfers_in = asset.transfer_logs.filter(status='COMPLETED', transfer_type='IN').aggregate(total=Sum('quantity'))['total'] or 0
    transfers_out = asset.transfer_logs.filter(status='COMPLETED', transfer_type='OUT').aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'asset': asset,
        'transactions': transactions,
        'purchases_total': purchases_total,
        'transfers_in': transfers_in,
        'transfers_out': transfers_out,
    }
    
    return render(request, 'assets/asset_detail.html', context)


@login_required
def transaction_log(request):
    """View audit log of all transactions"""
    transactions = TransactionLog.objects.select_related('asset', 'created_by').all()
    
    # Filter by transaction type
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by date
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        transactions = transactions.filter(created_at__date__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__date__lte=end_date)
    
    context = {
        'transactions': transactions,
    }
    
    return render(request, 'assets/transaction_log.html', context)


@login_required
def net_movement_detail(request, asset_id):
    """API endpoint for net movement details (popup)"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    # Check permissions
    if not request.user.is_superuser and not request.user.groups.filter(name='Logistics Officer').exists():
        if get_user_base(request.user) != asset.base:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    purchases = asset.purchases.filter(status='APPROVED').values('id', 'quantity', 'supplier', 'purchase_date')
    transfers_in = asset.transfer_logs.filter(status='COMPLETED', transfer_type='IN').values('id', 'quantity', 'created_at')
    transfers_out = asset.transfer_logs.filter(status='COMPLETED', transfer_type='OUT').values('id', 'quantity', 'created_at')
    
    data = {
        'asset': str(asset),
        'purchases': list(purchases),
        'transfers_in': list(transfers_in),
        'transfers_out': list(transfers_out),
        'net_movement': float(asset.calculate_net_movement()),
    }
    
    return JsonResponse(data)


# Delete Views
@login_required
@require_http_methods(["POST"])
def delete_purchase(request, purchase_id):
    """Delete a purchase"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    # Check permissions - only admin or the creator can delete
    if not request.user.is_superuser:
        return redirect('purchases')
    
    purchase.delete()
    return redirect('purchases')


@login_required
@require_http_methods(["POST"])
def delete_transfer(request, transfer_id):
    """Delete a transfer"""
    transfer = get_object_or_404(Transfer, id=transfer_id)
    
    # Check permissions - only admin can delete
    if not request.user.is_superuser:
        return redirect('transfers')
    
    transfer.delete()
    return redirect('transfers')


@login_required
@require_http_methods(["POST"])
def delete_assignment(request, assignment_id):
    """Delete an assignment"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check permissions - only admin can delete
    if not request.user.is_superuser:
        return redirect('assignments')
    
    assignment.delete()
    return redirect('assignments')


@login_required
@require_http_methods(["POST"])
def delete_expenditure(request, expenditure_id):
    """Delete an expenditure"""
    expenditure = get_object_or_404(Expenditure, id=expenditure_id)
    
    # Check permissions - only admin can delete
    if not request.user.is_superuser:
        return redirect('expenditures')
    
    expenditure.delete()
    return redirect('expenditures')
