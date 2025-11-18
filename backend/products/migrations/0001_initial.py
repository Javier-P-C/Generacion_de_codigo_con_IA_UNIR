from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('presentation', models.CharField(max_length=20, choices=[
                    ('tablets', 'Tablets'),
                    ('capsules', 'Capsules'),
                    ('syrups', 'Syrups'),
                    ('suspensions', 'Suspensions'),
                    ('solutions', 'Solutions'),
                    ('pills', 'Pills'),
                    ('injectables', 'Injectables'),
                ])),
                ('substance', models.CharField(max_length=150)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
    ]
