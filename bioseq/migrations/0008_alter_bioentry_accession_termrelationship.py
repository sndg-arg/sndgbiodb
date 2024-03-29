# Generated by Django 4.2.4 on 2023-08-22 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bioseq', '0007_alter_termdbxref_dbxref'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bioentry',
            name='accession',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.CreateModel(
            name='TermRelationship',
            fields=[
                ('term_relationship_id', models.AutoField(primary_key=True, serialize=False)),
                ('object_term', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='object_termrelationships', to='bioseq.term')),
                ('ontology', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.ontology')),
                ('predicate_term', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='predicate_termrelationships', to='bioseq.term')),
                ('subject_term', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='subject_termrelationships', to='bioseq.term')),
            ],
            options={
                'db_table': 'term_relationship',
                'managed': True,
                'unique_together': {('subject_term', 'predicate_term', 'object_term', 'ontology')},
            },
        ),
    ]
