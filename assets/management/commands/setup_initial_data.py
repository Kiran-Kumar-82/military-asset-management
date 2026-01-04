from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from assets.models import Base, EquipmentType


class Command(BaseCommand):
    help = 'Setup initial data and user roles for Military Asset Management System'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting initial setup...'))

        # Create groups
        self.stdout.write('Creating user roles...')
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        commander_group, _ = Group.objects.get_or_create(name='Base Commander')
        logistics_group, _ = Group.objects.get_or_create(name='Logistics Officer')
        
        # Assign permissions to Admin group (all permissions)
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)
        
        self.stdout.write(self.style.SUCCESS('✓ User roles created'))

        # Create base equipment types
        self.stdout.write('Creating equipment types...')
        equipment_types = [
            ('M4 Carbine', 'WEAPON', 'Assault rifle'),
            ('M16A4', 'WEAPON', 'Assault rifle'),
            ('Humvee', 'VEHICLE', 'Military utility vehicle'),
            ('M35 Truck', 'VEHICLE', 'Military cargo truck'),
            ('5.56mm Ammunition', 'AMMUNITION', 'Standard rifle ammunition'),
            ('7.62mm Ammunition', 'AMMUNITION', 'Rifle ammunition'),
            ('Body Armor', 'OTHER', 'Protective gear'),
            ('Helmet', 'OTHER', 'Combat helmet'),
        ]

        for name, category, description in equipment_types:
            EquipmentType.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': description,
                    'unit_of_measure': 'Unit' if category in ['VEHICLE', 'WEAPON'] else 'Box' if category == 'AMMUNITION' else 'Piece'
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Equipment types created'))

        # Create base military installations
        self.stdout.write('Creating military bases...')
        bases = [
            ('Fort Liberty', 'North Carolina, USA'),
            ('Fort Jackson', 'South Carolina, USA'),
            ('Fort Stewart', 'Georgia, USA'),
            ('Fort Benning', 'Georgia, USA'),
            ('Joint Base Lewis-McChord', 'Washington, USA'),
        ]

        base_objects = {}
        for base_name, location in bases:
            base_obj, _ = Base.objects.get_or_create(
                name=base_name,
                defaults={'location': location}
            )
            base_objects[base_name] = base_obj
        
        self.stdout.write(self.style.SUCCESS('✓ Military bases created'))

        # Create demo admin user
        self.stdout.write('Creating demo users...')
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@military.local',
                password='admin123'
            )
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('✓ Admin user created (username: admin, password: admin123)'))

        if not User.objects.filter(username='commander').exists():
            commander_user = User.objects.create_user(
                username='commander',
                email='commander@military.local',
                password='pass123'
            )
            commander_user.groups.add(commander_group)
            # Assign commander to Fort Liberty
            fort_liberty = base_objects.get('Fort Liberty')
            if fort_liberty:
                fort_liberty.commander = commander_user
                fort_liberty.save()
            self.stdout.write(self.style.SUCCESS('✓ Commander user created (username: commander, password: pass123) - Assigned to Fort Liberty'))

        if not User.objects.filter(username='logistics').exists():
            logistics_user = User.objects.create_user(
                username='logistics',
                email='logistics@military.local',
                password='pass123'
            )
            logistics_user.groups.add(logistics_group)
            self.stdout.write(self.style.SUCCESS('✓ Logistics user created (username: logistics, password: pass123)'))

        self.stdout.write(self.style.SUCCESS('\n✅ Setup completed successfully!'))
        self.stdout.write(self.style.WARNING('\n⚠️ IMPORTANT: Change demo passwords in production!'))
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Run: python manage.py runserver')
        self.stdout.write('2. Access: http://localhost:8000/accounts/login/')
        self.stdout.write('3. Login with demo credentials above')
        self.stdout.write('4. Create assets via admin panel at /admin/')
