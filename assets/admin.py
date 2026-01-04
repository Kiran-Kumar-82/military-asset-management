from django.contrib import admin
from django.utils.html import format_html
from assets.models import (
    Base, EquipmentType, Asset, Personnel, Purchase, 
    Transfer, Assignment, Expenditure, TransactionLog, TransferLog
)


@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'commander', 'created_at')
    search_fields = ('name', 'location')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit_of_measure')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('get_equipment', 'get_base', 'opening_balance', 'closing_balance', 'assigned_count', 'expended_count')
    list_filter = ('base', 'equipment_type', 'created_at')
    search_fields = ('equipment_type__name', 'base__name')
    readonly_fields = ('created_at', 'updated_at', 'calculate_net_movement')
    fieldsets = (
        ('Asset Information', {
            'fields': ('equipment_type', 'base')
        }),
        ('Balances', {
            'fields': ('opening_balance', 'closing_balance')
        }),
        ('Tracking', {
            'fields': ('assigned_count', 'expended_count', 'calculate_net_movement')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_equipment(self, obj):
        return obj.equipment_type.name
    get_equipment.short_description = 'Equipment'
    
    def get_base(self, obj):
        return obj.base.name
    get_base.short_description = 'Base'


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'rank', 'service_number', 'get_base')
    list_filter = ('base', 'rank')
    search_fields = ('user__first_name', 'user__last_name', 'service_number')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_name.short_description = 'Name'
    
    def get_base(self, obj):
        return obj.base.name
    get_base.short_description = 'Base'


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_asset', 'quantity', 'supplier', 'cost', 'status_badge', 'purchase_date')
    list_filter = ('status', 'purchase_date', 'asset__base')
    search_fields = ('reference_number', 'supplier', 'asset__equipment_type__name')
    readonly_fields = ('created_at', 'updated_at', 'purchase_date', 'approval_date')
    fieldsets = (
        ('Purchase Information', {
            'fields': ('asset', 'quantity', 'supplier', 'reference_number', 'cost')
        }),
        ('Status', {
            'fields': ('status', 'approved_by', 'approval_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'purchase_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_asset(self, obj):
        return str(obj.asset)
    get_asset.short_description = 'Asset'
    
    def status_badge(self, obj):
        colors = {'PENDING': '#FFA500', 'APPROVED': '#00AA00', 'REJECTED': '#FF0000'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#999'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipment_type', 'quantity', 'from_base', 'to_base', 'status_badge', 'initiated_date')
    list_filter = ('status', 'initiated_date')
    search_fields = ('reference_number', 'equipment_type__name')
    readonly_fields = ('created_at', 'updated_at', 'initiated_date')
    fieldsets = (
        ('Transfer Information', {
            'fields': ('equipment_type', 'quantity', 'from_base', 'to_base', 'reference_number')
        }),
        ('Status', {
            'fields': ('status', 'initiated_by', 'approved_by', 'initiated_date', 'completion_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFA500',
            'IN_TRANSIT': '#0099FF',
            'COMPLETED': '#00AA00',
            'REJECTED': '#FF0000'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#999'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_personnel', 'get_asset', 'quantity', 'assignment_date', 'get_status')
    list_filter = ('assignment_date', 'asset__base')
    search_fields = ('personnel__user__first_name', 'personnel__user__last_name', 'asset__equipment_type__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_personnel(self, obj):
        return str(obj.personnel)
    get_personnel.short_description = 'Personnel'
    
    def get_asset(self, obj):
        return str(obj.asset)
    get_asset.short_description = 'Asset'
    
    def get_status(self, obj):
        if obj.return_date:
            return 'Returned'
        return 'Active'
    get_status.short_description = 'Status'


@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_asset', 'quantity', 'reason', 'expended_date')
    list_filter = ('expended_date', 'asset__base')
    search_fields = ('reference_number', 'reason', 'asset__equipment_type__name')
    readonly_fields = ('created_at', 'updated_at', 'expended_date')
    
    def get_asset(self, obj):
        return str(obj.asset)
    get_asset.short_description = 'Asset'


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_asset', 'transaction_type', 'quantity', 'get_user', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('asset__equipment_type__name', 'created_by__username')
    readonly_fields = ('created_at', 'asset', 'transaction_type', 'quantity', 'created_by', 'ip_address', 'user_agent')
    
    def get_asset(self, obj):
        return str(obj.asset)
    get_asset.short_description = 'Asset'
    
    def get_user(self, obj):
        return obj.created_by.username if obj.created_by else 'System'
    get_user.short_description = 'User'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TransferLog)
class TransferLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset', 'transfer_type', 'quantity', 'status', 'created_at')
    list_filter = ('transfer_type', 'status', 'created_at')
    search_fields = ('asset__equipment_type__name',)
    readonly_fields = ('created_at', 'updated_at')
