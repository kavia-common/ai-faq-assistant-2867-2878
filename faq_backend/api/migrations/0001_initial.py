from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgeBaseEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('question', models.TextField(blank=True, default='')),
                ('answer', models.TextField()),
                ('tags', models.JSONField(blank=True, default=list)),
                ('source', models.CharField(blank=True, default='', max_length=255)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='QueryLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('question', models.TextField()),
                ('retrieved_context_ids', models.JSONField(blank=True, default=list)),
                ('answer', models.TextField(blank=True, default='')),
                ('latency_ms', models.IntegerField(default=0)),
                ('status', models.CharField(default='ok', max_length=32)),
                ('error', models.TextField(blank=True, default='')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='knowledgebaseentry',
            index=models.Index(fields=['is_active'], name='api_knowled_is_acti_42cf5a_idx'),
        ),
        migrations.AddIndex(
            model_name='knowledgebaseentry',
            index=models.Index(fields=['title'], name='api_knowled_title_c6a1e8_idx'),
        ),
        migrations.AddIndex(
            model_name='querylog',
            index=models.Index(fields=['created_at'], name='api_querylo_created_b3eb3f_idx'),
        ),
        migrations.AddIndex(
            model_name='querylog',
            index=models.Index(fields=['status'], name='api_querylo_status_9d97df_idx'),
        ),
    ]
