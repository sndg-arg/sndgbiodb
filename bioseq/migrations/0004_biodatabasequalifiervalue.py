# Generated by Django 4.0.6 on 2023-02-02 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bioseq', '0003_bioentrydbxref'),
    ]

    operations = [
        migrations.CreateModel(
            name='BiodatabaseQualifierValue',
            fields=[
                ('biodatabase_qualifiervalue_id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.TextField(blank=True, null=True)),
                ('rank', models.IntegerField(default=1, null=True)),
                ('biodatabase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qualifiers', to='bioseq.biodatabase')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.term')),
            ],
            options={
                'db_table': 'bioedatabase_qualifier_value',
                'managed': True,
                'unique_together': {('biodatabase', 'term', 'rank')},
            },
        ),
    ]
