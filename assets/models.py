from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Sum, F
from decimal import Decimal
from datetime import datetime


class Base(models.Model):
    """Military base/installation"""
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    commander = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='commanded_base')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bases'
        verbose_name_plural = 'Bases'

    def __str__(self):
        return self.name


class EquipmentType(models.Model):
    """Types of equipment (Vehicle, Weapon, Ammunition, etc.)"""
    CATEGORY_CHOICES = (
        ('VEHICLE', 'Vehicle'),
        ('WEAPON', 'Weapon'),
        ('AMMUNITION', 'Ammunition'),
        ('OTHER', 'Other'),
    )
    
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    unit_of_measure = models.CharField(max_length=50, default='Unit')  # Unit, Round, Box, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment_types'

    def __str__(self):
        return self.name


class Asset(models.Model):
    """Individual asset with opening and closing balances"""
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, related_name='assets')
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='assets')
    
    # Balances
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Tracking
    assigned_count = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expended_count = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assets'
        unique_together = ('equipment_type', 'base')

    def __str__(self):
        return f"{self.equipment_type.name} at {self.base.name}"

    def calculate_net_movement(self):
        """Calculate: Purchases + Transfers In - Transfers Out"""
        purchases = self.purchases.filter(status='APPROVED').aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        transfers_in = self.transfer_logs.filter(
            status='COMPLETED',
            transfer_type='IN'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        transfers_out = self.transfer_logs.filter(
            status='COMPLETED',
            transfer_type='OUT'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return Decimal(purchases) + Decimal(transfers_in) - Decimal(transfers_out)

    def update_closing_balance(self):
        """Update closing balance: opening + net movements - assigned - expended"""
        net_movement = self.calculate_net_movement()
        self.closing_balance = (
            self.opening_balance + net_movement - 
            self.assigned_count - self.expended_count
        )
        self.save()


class Personnel(models.Model):
    """Military personnel"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personnel')
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='personnel')
    rank = models.CharField(max_length=100)
    service_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personnel'
        verbose_name_plural = 'Personnel'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.rank})"


class Purchase(models.Model):
    """Track asset purchases"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    supplier = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=100, unique=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchases_created')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases_approved')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchases'
        ordering = ['-purchase_date']

    def __str__(self):
        return f"Purchase: {self.asset.equipment_type.name} ({self.quantity})"

    def approve(self, user):
        """Approve purchase and update asset balance"""
        if self.status == 'APPROVED':
            return
        
        self.status = 'APPROVED'
        self.approval_date = datetime.now()
        self.approved_by = user
        self.save()
        
        # Update asset closing balance
        self.asset.update_closing_balance()
        
        # Log transaction
        TransactionLog.objects.create(
            asset=self.asset,
            transaction_type='PURCHASE',
            quantity=self.quantity,
            related_object_id=self.id,
            created_by=user
        )


class Transfer(models.Model):
    """Asset transfers between bases"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    )
    
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, related_name='transfers')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    from_base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='transfers_out')
    to_base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='transfers_in')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    initiated_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    reference_number = models.CharField(max_length=100, unique=True)
    notes = models.TextField(blank=True)
    
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_initiated')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_approved')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transfers'
        ordering = ['-initiated_date']

    def __str__(self):
        return f"Transfer: {self.equipment_type.name} from {self.from_base.name} to {self.to_base.name}"

    def complete_transfer(self, user):
        """Complete transfer and update both asset balances"""
        if self.status == 'COMPLETED':
            return
        
        from_asset = Asset.objects.get(equipment_type=self.equipment_type, base=self.from_base)
        to_asset = Asset.objects.get(equipment_type=self.equipment_type, base=self.to_base)
        
        # Update balances
        from_asset.closing_balance -= self.quantity
        from_asset.save()
        
        to_asset.closing_balance += self.quantity
        to_asset.save()
        
        self.status = 'COMPLETED'
        self.completion_date = datetime.now()
        self.approved_by = user
        self.save()
        
        # Log transactions for both bases
        TransactionLog.objects.create(
            asset=from_asset,
            transaction_type='TRANSFER_OUT',
            quantity=self.quantity,
            related_object_id=self.id,
            created_by=user
        )
        
        TransactionLog.objects.create(
            asset=to_asset,
            transaction_type='TRANSFER_IN',
            quantity=self.quantity,
            related_object_id=self.id,
            created_by=user
        )


class TransferLog(models.Model):
    """Log individual transfer transactions"""
    TRANSFER_TYPES = (
        ('IN', 'Transfer In'),
        ('OUT', 'Transfer Out'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    )
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='transfer_logs')
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name='logs')
    transfer_type = models.CharField(max_length=10, choices=TRANSFER_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transfer_logs'

    def __str__(self):
        return f"{self.asset} - {self.transfer_type}: {self.quantity}"


class Assignment(models.Model):
    """Asset assignment to personnel"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='assignments')
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='assignments')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    assignment_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignments'
        ordering = ['-assignment_date']

    def __str__(self):
        return f"{self.personnel} - {self.asset.equipment_type.name}: {self.quantity}"

    def save(self, *args, **kwargs):
        """Update asset assigned count when assignment is created"""
        if not self.pk:  # New assignment
            self.asset.assigned_count += self.quantity
            self.asset.update_closing_balance()
        
        super().save(*args, **kwargs)
        
        # Log transaction
        TransactionLog.objects.create(
            asset=self.asset,
            transaction_type='ASSIGNMENT',
            quantity=self.quantity,
            related_object_id=self.id,
            created_by=self.assigned_by
        )

    def return_asset(self):
        """Return assigned asset"""
        if self.return_date:
            return
        
        self.return_date = datetime.now()
        self.asset.assigned_count -= self.quantity
        self.asset.update_closing_balance()
        self.save()


class Expenditure(models.Model):
    """Track expended/consumed assets"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='expenditures')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    expended_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=100, unique=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expenditures_recorded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expenditures'
        ordering = ['-expended_date']

    def __str__(self):
        return f"Expenditure: {self.asset.equipment_type.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        """Update asset expended count when expenditure is recorded"""
        if not self.pk:  # New expenditure
            self.asset.expended_count += self.quantity
            self.asset.update_closing_balance()
        
        super().save(*args, **kwargs)
        
        # Log transaction
        TransactionLog.objects.create(
            asset=self.asset,
            transaction_type='EXPENDITURE',
            quantity=self.quantity,
            related_object_id=self.id,
            created_by=self.recorded_by
        )


class TransactionLog(models.Model):
    """Audit log for all transactions"""
    TRANSACTION_TYPES = (
        ('PURCHASE', 'Purchase'),
        ('TRANSFER_IN', 'Transfer In'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('ASSIGNMENT', 'Assignment'),
        ('EXPENDITURE', 'Expenditure'),
        ('OPENING_BALANCE', 'Opening Balance'),
    )
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='transaction_logs')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transaction_logs')
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'transaction_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset', '-created_at']),
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.asset}: {self.quantity}"
