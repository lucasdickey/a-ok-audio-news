# Generated by Django 4.2.21 on 2025-05-21 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digests', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dailydigest',
            old_name='gpt_prompt',
            new_name='llm_prompt',
        ),
        migrations.RemoveField(
            model_name='dailydigest',
            name='gpt_response_raw',
        ),
        migrations.AddField(
            model_name='dailydigest',
            name='llm_response_raw',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailydigest',
            name='audio_url_en',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailydigest',
            name='audio_url_zh',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailydigest',
            name='description_zh',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailydigest',
            name='keywords_en',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dailydigest',
            name='keywords_zh',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dailydigest',
            name='summary_text_zh',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dailydigest',
            name='title_zh',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
