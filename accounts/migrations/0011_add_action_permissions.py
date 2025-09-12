from django.db import migrations

def add_action_permissions(apps, schema_editor):
    ActionPermission = apps.get_model('accounts', 'ActionPermission')
    ActionPermission.objects.get_or_create(action_name='generate_api_key', defaults={'min_role': 'admin'})
    ActionPermission.objects.get_or_create(action_name='view_api_key', defaults={'min_role': 'admin'})
    ActionPermission.objects.get_or_create(action_name='delete_api_key', defaults={'min_role': 'admin'})

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0010_apikey'),  # Matches your latest migration
    ]
    operations = [
        migrations.RunPython(add_action_permissions, reverse_code=migrations.RunPython.noop),
    ]