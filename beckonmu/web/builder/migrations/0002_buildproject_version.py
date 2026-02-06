# Generated manually for optimistic concurrency version field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("builder", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="buildproject",
            name="version",
            field=models.PositiveIntegerField(
                default=1,
                help_text="Optimistic concurrency version -- incremented on each save",
            ),
        ),
    ]
