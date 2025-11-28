# Generated manually - Reorganize credit packages
from django.db import migrations


def update_packages(apps, schema_editor):
    """Reorganize credit packages with new names"""
    CreditPackage = apps.get_model('users', 'CreditPackage')

    # Delete all existing packages
    CreditPackage.objects.all().delete()

    # Create new package structure
    packages = [
        {
            'name': 'Starter Pack',
            'credits': 1,
            'price': 0.99,
            'display_order': 1,
            'is_popular': False,
        },
        {
            'name': 'Value Pack',
            'credits': 10,
            'price': 9.99,
            'display_order': 2,
            'is_popular': False,
        },
        {
            'name': 'Popular Pack',
            'credits': 25,
            'price': 19.99,
            'display_order': 3,
            'is_popular': True,
        },
        {
            'name': 'Pro Pack',
            'credits': 50,
            'price': 34.99,
            'display_order': 4,
            'is_popular': False,
        },
    ]

    for package_data in packages:
        CreditPackage.objects.create(
            name=package_data['name'],
            credits=package_data['credits'],
            price=package_data['price'],
            display_order=package_data['display_order'],
            is_popular=package_data['is_popular'],
            is_active=True,
        )


def reverse_update_packages(apps, schema_editor):
    """Restore original package structure"""
    CreditPackage = apps.get_model('users', 'CreditPackage')

    # Delete current packages
    CreditPackage.objects.all().delete()

    # Restore original packages
    packages = [
        {
            'name': 'Starter Pack',
            'credits': 10,
            'price': 9.99,
            'display_order': 1,
            'is_popular': False,
        },
        {
            'name': 'Popular Pack',
            'credits': 25,
            'price': 19.99,
            'display_order': 2,
            'is_popular': True,
        },
        {
            'name': 'Pro Pack',
            'credits': 50,
            'price': 34.99,
            'display_order': 3,
            'is_popular': False,
        },
        {
            'name': 'Ultimate Pack',
            'credits': 100,
            'price': 59.99,
            'display_order': 4,
            'is_popular': False,
        },
    ]

    for package_data in packages:
        CreditPackage.objects.create(
            name=package_data['name'],
            credits=package_data['credits'],
            price=package_data['price'],
            display_order=package_data['display_order'],
            is_popular=package_data['is_popular'],
            is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_populate_credit_packages'),
    ]

    operations = [
        migrations.RunPython(update_packages, reverse_update_packages),
    ]
