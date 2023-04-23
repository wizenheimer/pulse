# Generated by Django 4.2 on 2023-04-23 06:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
        ('users', '0002_alter_user_teams_monitorassignment_user_monitors'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriberAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fetch_uptime', models.BooleanField(default=False)),
                ('fetch_port', models.BooleanField(default=False)),
                ('fetch_ssl', models.BooleanField(default=False)),
                ('fetch_speed', models.BooleanField(default=False)),
                ('monitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitor.monitor')),
                ('subscriber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.subscriber')),
            ],
        ),
        migrations.AddField(
            model_name='subscriber',
            name='monitors',
            field=models.ManyToManyField(related_name='subscribers', through='users.SubscriberAssignment', to='monitor.monitor'),
        ),
    ]
