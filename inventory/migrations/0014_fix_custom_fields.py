from django.db import migrations, models

def populate_custom_fields(apps, schema_editor):
    Item = apps.get_model('inventory', 'Item')
    for item in Item.objects.all():
        if not hasattr(item, 'custom_fields') or item.custom_fields is None:
            item.custom_fields = {}
        item.save()

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0013_locationevent_raw_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='Item',
            name='custom_fields',
            field=models.JSONField(default=dict, null=True),
            preserve_default=False,
        ),
        migrations.RunPython(populate_custom_fields),
        migrations.AlterField(
            model_name='Item',
            name='custom_fields',
            field=models.JSONField(default=dict),
        ),
    ]