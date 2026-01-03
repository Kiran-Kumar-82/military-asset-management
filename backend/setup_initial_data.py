#!/usr/bin/env python
"""
Script to set up initial data for MAMS
Run this after migrations: python manage.py shell < setup_initial_data.py
Or: python manage.py runscript setup_initial_data (if using django-extensions)
"""

from accounts.models import Role, User
from assets.models import Base, AssetType

# Create Roles
print("Creating roles...")
admin_role, _ = Role.objects.get_or_create(
    name=Role.ADMIN,
    defaults={'description': 'System Administrator - Full access'}
)
base_commander_role, _ = Role.objects.get_or_create(
    name=Role.BASE_COMMANDER,
    defaults={'description': 'Base Commander - Access to assigned base only'}
)
logistics_officer_role, _ = Role.objects.get_or_create(
    name=Role.LOGISTICS_OFFICER,
    defaults={'description': 'Logistics Officer - Can manage purchases and transfers'}
)
print("✓ Roles created")

# Create sample bases (optional - remove if not needed)
print("\nCreating sample bases...")
base1, _ = Base.objects.get_or_create(
    code='BASE001',
    defaults={
        'name': 'Alpha Base',
        'location': 'Location A',
        'description': 'Primary military base'
    }
)
base2, _ = Base.objects.get_or_create(
    code='BASE002',
    defaults={
        'name': 'Beta Base',
        'location': 'Location B',
        'description': 'Secondary military base'
    }
)
print("✓ Sample bases created")

# Create sample asset types (optional - remove if not needed)
print("\nCreating sample asset types...")
AssetType.objects.get_or_create(
    name='M4 Rifle',
    defaults={
        'category': 'Weapon',
        'description': 'Standard issue rifle',
        'unit': 'unit'
    }
)
AssetType.objects.get_or_create(
    name='5.56mm Ammunition',
    defaults={
        'category': 'Ammunition',
        'description': 'Standard ammunition',
        'unit': 'round'
    }
)
AssetType.objects.get_or_create(
    name='Humvee',
    defaults={
        'category': 'Vehicle',
        'description': 'Military vehicle',
        'unit': 'unit'
    }
)
print("✓ Sample asset types created")

print("\n✓ Initial data setup complete!")
print("\nNext steps:")
print("1. Create a superuser: python manage.py createsuperuser")
print("2. Assign roles to users via Django admin or API")


