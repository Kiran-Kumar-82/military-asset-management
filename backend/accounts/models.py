"""
User and Role models for RBAC
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """Role model for RBAC"""
    ADMIN = 'admin'
    BASE_COMMANDER = 'base_commander'
    LOGISTICS_OFFICER = 'logistics_officer'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (BASE_COMMANDER, 'Base Commander'),
        (LOGISTICS_OFFICER, 'Logistics Officer'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        db_table = 'roles'


class User(AbstractUser):
    """Custom User model with role and base assignment"""
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    assigned_base = models.ForeignKey(
        'assets.Base',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personnel'
    )
    
    class Meta:
        db_table = 'users'
    
    def is_admin(self):
        return self.role and self.role.name == Role.ADMIN
    
    def is_base_commander(self):
        return self.role and self.role.name == Role.BASE_COMMANDER
    
    def is_logistics_officer(self):
        return self.role and self.role.name == Role.LOGISTICS_OFFICER


