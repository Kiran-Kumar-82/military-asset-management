"""
Signals for automatic audit logging
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Purchase, Transfer, Assignment, Expenditure
from audit.models import AuditLog


@receiver(post_save, sender=Purchase)
def log_purchase(sender, instance, created, **kwargs):
    """Log purchase creation/update"""
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        action=action,
        model_name='Purchase',
        object_id=instance.id,
        details=f"Purchase: {instance.quantity} {instance.asset_type.name} at {instance.base.name}",
        user=instance.created_by
    )


@receiver(post_save, sender=Transfer)
def log_transfer(sender, instance, created, **kwargs):
    """Log transfer creation/update"""
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        action=action,
        model_name='Transfer',
        object_id=instance.id,
        details=f"Transfer: {instance.quantity} {instance.asset_type.name} from {instance.source_base.name} to {instance.destination_base.name}",
        user=instance.created_by
    )


@receiver(post_save, sender=Assignment)
def log_assignment(sender, instance, created, **kwargs):
    """Log assignment creation/update"""
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        action=action,
        model_name='Assignment',
        object_id=instance.id,
        details=f"Assignment: {instance.quantity} {instance.asset_type.name} to {instance.assigned_to} at {instance.base.name}",
        user=instance.created_by
    )


@receiver(post_save, sender=Expenditure)
def log_expenditure(sender, instance, created, **kwargs):
    """Log expenditure creation/update"""
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        action=action,
        model_name='Expenditure',
        object_id=instance.id,
        details=f"Expenditure: {instance.quantity} {instance.asset_type.name} at {instance.base.name}",
        user=instance.created_by
    )


@receiver(post_delete, sender=Purchase)
def log_purchase_delete(sender, instance, **kwargs):
    """Log purchase deletion"""
    AuditLog.objects.create(
        action='DELETE',
        model_name='Purchase',
        object_id=instance.id,
        details=f"Purchase deleted: {instance.quantity} {instance.asset_type.name} at {instance.base.name}",
        user=None
    )


@receiver(post_delete, sender=Transfer)
def log_transfer_delete(sender, instance, **kwargs):
    """Log transfer deletion"""
    AuditLog.objects.create(
        action='DELETE',
        model_name='Transfer',
        object_id=instance.id,
        details=f"Transfer deleted: {instance.quantity} {instance.asset_type.name}",
        user=None
    )


@receiver(post_delete, sender=Assignment)
def log_assignment_delete(sender, instance, **kwargs):
    """Log assignment deletion"""
    AuditLog.objects.create(
        action='DELETE',
        model_name='Assignment',
        object_id=instance.id,
        details=f"Assignment deleted: {instance.quantity} {instance.asset_type.name}",
        user=None
    )


@receiver(post_delete, sender=Expenditure)
def log_expenditure_delete(sender, instance, **kwargs):
    """Log expenditure deletion"""
    AuditLog.objects.create(
        action='DELETE',
        model_name='Expenditure',
        object_id=instance.id,
        details=f"Expenditure deleted: {instance.quantity} {instance.asset_type.name}",
        user=None
    )


