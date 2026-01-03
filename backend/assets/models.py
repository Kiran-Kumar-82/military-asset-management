"""
Core models for Asset Management System
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from audit.models import AuditLog


class Base(models.Model):
    """Military Base model"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        db_table = 'bases'
        ordering = ['name']


class AssetType(models.Model):
    """Asset Type model (e.g., Vehicle, Weapon, Ammunition)"""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)  # e.g., "Vehicle", "Weapon", "Ammunition"
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50, default='unit')  # e.g., "unit", "round", "kg"
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    class Meta:
        db_table = 'asset_types'
        ordering = ['category', 'name']


class Asset(models.Model):
    """Asset inventory model - tracks current inventory per base and asset type"""
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='assets')
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assets'
        unique_together = ['base', 'asset_type']
        ordering = ['base', 'asset_type']
    
    def __str__(self):
        return f"{self.asset_type.name} at {self.base.name}: {self.quantity}"


class Purchase(models.Model):
    """Purchase record - assets purchased for a base"""
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='purchases')
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    purchase_date = models.DateField()
    purchase_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    supplier = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='purchases_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'purchases'
        ordering = ['-purchase_date', '-created_at']
    
    def __str__(self):
        return f"Purchase: {self.quantity} {self.asset_type.name} at {self.base.name} on {self.purchase_date}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update asset inventory
        asset, created = Asset.objects.get_or_create(
            base=self.base,
            asset_type=self.asset_type,
            defaults={'quantity': 0}
        )
        asset.quantity += self.quantity
        asset.save()


class Transfer(models.Model):
    """Transfer record - assets transferred between bases"""
    source_base = models.ForeignKey(
        Base,
        on_delete=models.CASCADE,
        related_name='transfers_out'
    )
    destination_base = models.ForeignKey(
        Base,
        on_delete=models.CASCADE,
        related_name='transfers_in'
    )
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='transfers')
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    transfer_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfers_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transfers'
        ordering = ['-transfer_date', '-created_at']
    
    def __str__(self):
        return f"Transfer: {self.quantity} {self.asset_type.name} from {self.source_base.name} to {self.destination_base.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update source base inventory (decrease)
        source_asset, created = Asset.objects.get_or_create(
            base=self.source_base,
            asset_type=self.asset_type,
            defaults={'quantity': 0}
        )
        if source_asset.quantity < self.quantity:
            raise ValueError(f"Insufficient inventory at {self.source_base.name}")
        source_asset.quantity -= self.quantity
        source_asset.save()
        
        # Update destination base inventory (increase)
        dest_asset, created = Asset.objects.get_or_create(
            base=self.destination_base,
            asset_type=self.asset_type,
            defaults={'quantity': 0}
        )
        dest_asset.quantity += self.quantity
        dest_asset.save()


class Assignment(models.Model):
    """Assignment record - assets assigned to personnel or units"""
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='assignments')
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='assignments')
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    assigned_to = models.CharField(max_length=200)  # Personnel name or unit identifier
    assignment_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('returned', 'Returned'),
            ('lost', 'Lost'),
        ],
        default='active'
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'assignments'
        ordering = ['-assignment_date', '-created_at']
    
    def __str__(self):
        return f"Assignment: {self.quantity} {self.asset_type.name} to {self.assigned_to} at {self.base.name}"


class Expenditure(models.Model):
    """Expenditure record - assets expended/consumed"""
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='expenditures')
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='expenditures')
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    expenditure_date = models.DateField()
    reason = models.CharField(max_length=200)  # e.g., "Training", "Combat", "Maintenance"
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='expenditures_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'expenditures'
        ordering = ['-expenditure_date', '-created_at']
    
    def __str__(self):
        return f"Expenditure: {self.quantity} {self.asset_type.name} at {self.base.name} on {self.expenditure_date}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update asset inventory (decrease)
        asset, created = Asset.objects.get_or_create(
            base=self.base,
            asset_type=self.asset_type,
            defaults={'quantity': 0}
        )
        if asset.quantity < self.quantity:
            raise ValueError(f"Insufficient inventory at {self.base.name}")
        asset.quantity -= self.quantity
        asset.save()


