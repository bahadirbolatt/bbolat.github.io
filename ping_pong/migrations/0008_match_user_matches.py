# Generated by Django 4.1.4 on 2024-03-30 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ping_pong', '0007_delete_friendlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player1', models.CharField(max_length=100)),
                ('player2', models.CharField(max_length=100)),
                ('score', models.CharField(max_length=10)),
                ('result', models.CharField(choices=[('win', 'Win'), ('loss', 'Loss'), ('draw', 'Draw')], max_length=10)),
                ('match_date', models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='matches',
            field=models.ManyToManyField(blank=True, related_name='player_matches', to='ping_pong.match'),
        ),
    ]