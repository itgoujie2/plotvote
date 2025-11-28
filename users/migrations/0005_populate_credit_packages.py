# Generated manually - Data migration to populate credit packages
from django.db import migrations


def create_credit_packages(apps, schema_editor):
    """Create default credit packages"""
    CreditPackage = apps.get_model('users', 'CreditPackage')

    packages = [
        {
            'name': 'Starter Pack',
            'credits': 10,
            'price': 9.99,
            'display_order': 1,
            'is_popular': False,
            'is_active': True,
        },
        {
            'name': 'Popular Pack',
            'credits': 25,
            'price': 19.99,
            'display_order': 2,
            'is_popular': True,
            'is_active': True,
        },
        {
            'name': 'Pro Pack',
            'credits': 50,
            'price': 34.99,
            'display_order': 3,
            'is_popular': False,
            'is_active': True,
        },
        {
            'name': 'Ultimate Pack',
            'credits': 100,
            'price': 59.99,
            'display_order': 4,
            'is_popular': False,
            'is_active': True,
        },
    ]

    for package_data in packages:
        CreditPackage.objects.get_or_create(
            name=package_data['name'],
            defaults={
                'credits': package_data['credits'],
                'price': package_data['price'],
                'display_order': package_data['display_order'],
                'is_popular': package_data['is_popular'],
                'is_active': package_data['is_active'],
            }
        )


def remove_credit_packages(apps, schema_editor):
    """Remove credit packages (for migration rollback)"""
    CreditPackage = apps.get_model('users', 'CreditPackage')
    package_names = ['Starter Pack', 'Popular Pack', 'Pro Pack', 'Ultimate Pack']
    CreditPackage.objects.filter(name__in=package_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_subscriptionplan_usersubscription_adview'),
    ]

    operations = [
        migrations.RunPython(create_credit_packages, remove_credit_packages),
    ]
