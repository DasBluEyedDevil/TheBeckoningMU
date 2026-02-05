# Generated migration for BuildProject connection fields

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("builder", "0003_buildproject_status_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="buildproject",
            name="connection_room_id",
            field=models.IntegerField(
                blank=True,
                null=True,
                help_text="Live room dbref to connect this build to",
            ),
        ),
        migrations.AddField(
            model_name="buildproject",
            name="connection_direction",
            field=models.CharField(
                blank=True,
                max_length=10,
                null=True,
                help_text="Direction from live room into this build (n/s/e/w/ne/nw/se/sw/u/d)",
            ),
        ),
    ]
