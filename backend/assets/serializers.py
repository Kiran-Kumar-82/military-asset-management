"""
Serializers for Asset Management models
"""
from rest_framework import serializers
from .models import Base, AssetType, Asset, Purchase, Transfer, Assignment, Expenditure


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = ['id', 'name', 'code', 'location', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = ['id', 'name', 'category', 'description', 'unit', 'created_at']
        read_only_fields = ['created_at']


class AssetSerializer(serializers.ModelSerializer):
    base_name = serializers.CharField(source='base.name', read_only=True)
    asset_type_name = serializers.CharField(source='asset_type.name', read_only=True)
    asset_type_category = serializers.CharField(source='asset_type.category', read_only=True)
    
    class Meta:
        model = Asset
        fields = ['id', 'base', 'base_name', 'asset_type', 'asset_type_name', 
                  'asset_type_category', 'quantity', 'last_updated']
        read_only_fields = ['last_updated']


class PurchaseSerializer(serializers.ModelSerializer):
    base_name = serializers.CharField(source='base.name', read_only=True)
    asset_type_name = serializers.CharField(source='asset_type.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Purchase
        fields = ['id', 'base', 'base_name', 'asset_type', 'asset_type_name', 
                  'quantity', 'purchase_date', 'purchase_cost', 'supplier', 
                  'notes', 'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class TransferSerializer(serializers.ModelSerializer):
    source_base_name = serializers.CharField(source='source_base.name', read_only=True)
    destination_base_name = serializers.CharField(source='destination_base.name', read_only=True)
    asset_type_name = serializers.CharField(source='asset_type.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Transfer
        fields = ['id', 'source_base', 'source_base_name', 'destination_base', 
                  'destination_base_name', 'asset_type', 'asset_type_name', 
                  'quantity', 'transfer_date', 'notes', 'created_by', 
                  'created_by_username', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class AssignmentSerializer(serializers.ModelSerializer):
    base_name = serializers.CharField(source='base.name', read_only=True)
    asset_type_name = serializers.CharField(source='asset_type.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Assignment
        fields = ['id', 'base', 'base_name', 'asset_type', 'asset_type_name', 
                  'quantity', 'assigned_to', 'assignment_date', 'return_date', 
                  'status', 'notes', 'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class ExpenditureSerializer(serializers.ModelSerializer):
    base_name = serializers.CharField(source='base.name', read_only=True)
    asset_type_name = serializers.CharField(source='asset_type.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Expenditure
        fields = ['id', 'base', 'base_name', 'asset_type', 'asset_type_name', 
                  'quantity', 'expenditure_date', 'reason', 'notes', 
                  'created_by', 'created_by_username', 'created_at']
        read_only_fields = ['created_by', 'created_at']


