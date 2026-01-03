from django.contrib import admin
from .models import Base, AssetType, Asset, Purchase, Transfer, Assignment, Expenditure


@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location', 'created_at')
    search_fields = ('name', 'code', 'location')
    list_filter = ('created_at',)


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'created_at')
    search_fields = ('name', 'category')
    list_filter = ('category',)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('base', 'asset_type', 'quantity', 'last_updated')
    search_fields = ('base__name', 'asset_type__name')
    list_filter = ('base', 'asset_type', 'last_updated')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('base', 'asset_type', 'quantity', 'purchase_date', 'created_by', 'created_at')
    search_fields = ('base__name', 'asset_type__name', 'supplier')
    list_filter = ('purchase_date', 'base', 'asset_type', 'created_at')
    date_hierarchy = 'purchase_date'


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('source_base', 'destination_base', 'asset_type', 'quantity', 'transfer_date', 'created_by')
    search_fields = ('source_base__name', 'destination_base__name', 'asset_type__name')
    list_filter = ('transfer_date', 'source_base', 'destination_base', 'asset_type')
    date_hierarchy = 'transfer_date'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('base', 'asset_type', 'quantity', 'assigned_to', 'assignment_date', 'status', 'created_by')
    search_fields = ('base__name', 'asset_type__name', 'assigned_to')
    list_filter = ('status', 'assignment_date', 'base', 'asset_type')
    date_hierarchy = 'assignment_date'


@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ('base', 'asset_type', 'quantity', 'expenditure_date', 'reason', 'created_by')
    search_fields = ('base__name', 'asset_type__name', 'reason', 'notes')
    list_filter = ('expenditure_date', 'base', 'asset_type', 'reason')
    date_hierarchy = 'expenditure_date'


