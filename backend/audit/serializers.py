"""
Serializers for Audit Log
"""
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'model_name', 'object_id', 'details', 
                  'user', 'user_username', 'ip_address', 'user_agent', 'timestamp']
        read_only_fields = ['id', 'timestamp']


