# Generated by Django 4.0.6 on 2023-02-01 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Biodatabase',
            fields=[
                ('biodatabase_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('authority', models.CharField(blank=True, max_length=128, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'biodatabase',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Bioentry',
            fields=[
                ('bioentry_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('accession', models.CharField(max_length=128)),
                ('identifier', models.CharField(blank=True, max_length=40, null=True)),
                ('division', models.CharField(blank=True, max_length=6, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('version', models.PositiveSmallIntegerField(default=1, null=True)),
                ('index_updated', models.BooleanField(default=False)),
                ('biodatabase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='bioseq.biodatabase')),
            ],
            options={
                'db_table': 'bioentry',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Dbxref',
            fields=[
                ('dbxref_id', models.AutoField(primary_key=True, serialize=False)),
                ('dbname', models.CharField(max_length=40)),
                ('accession', models.CharField(max_length=128)),
                ('version', models.PositiveSmallIntegerField(default=1, null=True)),
            ],
            options={
                'db_table': 'dbxref',
                'managed': True,
                'unique_together': {('accession', 'dbname', 'version')},
            },
        ),
        migrations.CreateModel(
            name='Ontology',
            fields=[
                ('ontology_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, unique=True)),
                ('definition', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ontology',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('taxon_id', models.AutoField(primary_key=True, serialize=False)),
                ('ncbi_taxon_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('node_rank', models.CharField(blank=True, max_length=32, null=True)),
                ('genetic_code', models.PositiveIntegerField(blank=True, null=True)),
                ('mito_genetic_code', models.PositiveIntegerField(blank=True, null=True)),
                ('left_value', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('right_value', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('parent_taxon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children', to='bioseq.taxon')),
            ],
            options={
                'db_table': 'taxon',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('term_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
                ('definition', models.TextField(blank=True, null=True)),
                ('identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('is_obsolete', models.CharField(blank=True, max_length=1, null=True)),
                ('version', models.PositiveSmallIntegerField(default=1, null=True)),
                ('ontology', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='terms', to='bioseq.ontology')),
            ],
            options={
                'db_table': 'term',
                'managed': True,
                'unique_together': {('identifier', 'ontology', 'is_obsolete')},
            },
        ),
        migrations.CreateModel(
            name='Biosequence',
            fields=[
                ('bioentry', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='seq', serialize=False, to='bioseq.bioentry')),
                ('version', models.SmallIntegerField(blank=True, default=1, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('alphabet', models.CharField(blank=True, max_length=10, null=True)),
                ('seq', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'biosequence',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TaxIdx',
            fields=[
                ('tax', models.OneToOneField(db_column='tax_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='keywords', serialize=False, to='bioseq.taxon')),
                ('text', models.TextField()),
                ('genus', models.CharField(max_length=255)),
                ('family', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'tax_idx',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TermIdx',
            fields=[
                ('term', models.OneToOneField(db_column='term_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='keywords', serialize=False, to='bioseq.term')),
                ('text', models.TextField()),
            ],
            options={
                'db_table': 'term_idx',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Seqfeature',
            fields=[
                ('seqfeature_id', models.AutoField(primary_key=True, serialize=False)),
                ('display_name', models.CharField(blank=True, max_length=64, null=True)),
                ('rank', models.PositiveSmallIntegerField(default=1, null=True)),
                ('index_updated', models.BooleanField(default=False)),
                ('bioentry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='bioseq.bioentry')),
                ('source_term', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='source_of', to='bioseq.term')),
                ('type_term', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='features_of_type', to='bioseq.term')),
            ],
            options={
                'db_table': 'seqfeature',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='bioentry',
            name='taxon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.taxon'),
        ),
        migrations.CreateModel(
            name='TermDbxref',
            fields=[
                ('term_dbxref_id', models.AutoField(primary_key=True, serialize=False)),
                ('rank', models.SmallIntegerField(default=1, null=True)),
                ('dbxref', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.dbxref')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dbxrefs', to='bioseq.term')),
            ],
            options={
                'db_table': 'term_dbxref',
                'managed': True,
                'unique_together': {('term', 'dbxref')},
            },
        ),
        migrations.CreateModel(
            name='TaxonName',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('name_class', models.CharField(max_length=32)),
                ('taxon', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='names', to='bioseq.taxon')),
            ],
            options={
                'db_table': 'taxon_name',
                'managed': True,
                'unique_together': {('taxon', 'name', 'name_class')},
            },
        ),
        migrations.CreateModel(
            name='SeqfeatureDbxref',
            fields=[
                ('seqfeature_dbxref_id', models.AutoField(primary_key=True, serialize=False)),
                ('rank', models.SmallIntegerField(default=1, null=True)),
                ('dbxref', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.dbxref')),
                ('seqfeature', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='dbxrefs', to='bioseq.seqfeature')),
            ],
            options={
                'db_table': 'seqfeature_dbxref',
                'managed': True,
                'unique_together': {('seqfeature', 'dbxref')},
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('location_id', models.AutoField(primary_key=True, serialize=False)),
                ('start_pos', models.IntegerField(blank=True, null=True)),
                ('end_pos', models.IntegerField(blank=True, null=True)),
                ('strand', models.IntegerField()),
                ('rank', models.SmallIntegerField(default=1, null=True)),
                ('dbxref', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.dbxref')),
                ('seqfeature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='bioseq.seqfeature')),
                ('term', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.term')),
            ],
            options={
                'db_table': 'location',
                'managed': True,
                'unique_together': {('seqfeature', 'rank')},
            },
        ),
        migrations.CreateModel(
            name='BioentryQualifierValue',
            fields=[
                ('bioentry_qualifiervalue_id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.TextField(blank=True, null=True)),
                ('rank', models.IntegerField(default=1, null=True)),
                ('bioentry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qualifiers', to='bioseq.bioentry')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.term')),
            ],
            options={
                'db_table': 'bioentry_qualifier_value',
                'managed': True,
                'unique_together': {('bioentry', 'term', 'rank')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='bioentry',
            unique_together={('accession', 'biodatabase', 'version'), ('identifier', 'biodatabase')},
        ),
        migrations.CreateModel(
            name='DbxrefQualifierValue',
            fields=[
                ('dbxref', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bioseq.dbxref')),
                ('rank', models.SmallIntegerField(default=1, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='bioseq.term')),
            ],
            options={
                'db_table': 'dbxref_qualifier_value',
                'managed': True,
                'unique_together': {('dbxref', 'term', 'rank')},
            },
        ),
    ]
