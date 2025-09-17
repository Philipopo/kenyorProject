from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0011_remove_stockrecord_category_and_more'),  # Correct dependency
    ]

    operations = [
        # Rename the existing table
        migrations.RunSQL(
            sql="ALTER TABLE inventory_locationevent RENAME TO inventory_locationevent_old;",
            reverse_sql="ALTER TABLE inventory_locationevent_old RENAME TO inventory_locationevent;"
        ),
        # Create new table with raw_location nullable
        migrations.RunSQL(
            sql="""
            CREATE TABLE inventory_locationevent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event VARCHAR(20) NOT NULL,
                timestamp DATETIME NOT NULL,
                processed BOOLEAN NOT NULL,
                created_at DATETIME NOT NULL,
                quantity INTEGER NOT NULL,
                raw_location VARCHAR(100),  -- Nullable
                item_id INTEGER NOT NULL,
                storage_bin_id INTEGER NOT NULL,
                FOREIGN KEY (item_id) REFERENCES inventory_item(id),
                FOREIGN KEY (storage_bin_id) REFERENCES inventory_storagebin(id)
            );
            """,
            reverse_sql="DROP TABLE inventory_locationevent;"
        ),
        # Copy data from old table to new table
        migrations.RunSQL(
            sql="""
            INSERT INTO inventory_locationevent (
                id, event, timestamp, processed, created_at, quantity, item_id, storage_bin_id, raw_location
            )
            SELECT id, event, timestamp, processed, created_at, quantity, item_id, storage_bin_id, raw_location
            FROM inventory_locationevent_old;
            """,
            reverse_sql=""
        ),
        # Drop the old table
        migrations.RunSQL(
            sql="DROP TABLE inventory_locationevent_old;",
            reverse_sql=""
        ),
    ]