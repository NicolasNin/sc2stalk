# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 22:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Games',
            fields=[
                ('idgames', models.AutoField(db_column='idGames', primary_key=True, serialize=False)),
                ('path', models.CharField(blank=True, max_length=45, null=True)),
                ('server', models.CharField(blank=True, max_length=45, null=True)),
                ('map', models.CharField(blank=True, max_length=45, null=True)),
                ('type', models.CharField(blank=True, max_length=45, null=True)),
                ('decision', models.CharField(blank=True, max_length=45, null=True)),
                ('speed', models.CharField(blank=True, max_length=45, null=True)),
                ('date', models.IntegerField(blank=True, null=True)),
                ('guessopid', models.IntegerField(blank=True, db_column='GuessOpId', null=True)),
                ('guessopgameid', models.IntegerField(blank=True, db_column='GuessOpGameId', null=True)),
                ('current_mmr', models.CharField(blank=True, db_column='Current_MMR', max_length=45, null=True)),
                ('guessmmrchange', models.IntegerField(blank=True, db_column='GuessMMRChange', null=True)),
                ('current_rank', models.IntegerField(blank=True, db_column='Current_Rank', null=True)),
                ('current_league', models.CharField(blank=True, db_column='Current_league', max_length=45, null=True)),
                ('current_win', models.IntegerField(blank=True, db_column='Current_win', null=True)),
                ('current_losses', models.IntegerField(blank=True, db_column='Current_losses', null=True)),
                ('current_ties', models.IntegerField(blank=True, db_column='Current_ties', null=True)),
                ('current_points', models.CharField(blank=True, db_column='Current_Points', max_length=45, null=True)),
                ('guessptschange', models.IntegerField(blank=True, db_column='GuessPtsChange', null=True)),
                ('ranked', models.CharField(blank=True, max_length=10, null=True)),
                ('current_win_streak', models.IntegerField(blank=True, null=True)),
                ('lastplayed_date', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Games',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('idleague', models.AutoField(primary_key=True, serialize=False)),
                ('ladderid', models.IntegerField(blank=True, null=True, unique=True)),
                ('season', models.IntegerField(blank=True, null=True)),
                ('level', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Players',
            fields=[
                ('idplayer', models.AutoField(db_column='idPlayer', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=45, null=True)),
                ('server', models.CharField(blank=True, max_length=45, null=True)),
                ('rating', models.IntegerField(blank=True, null=True)),
                ('points', models.IntegerField(blank=True, null=True)),
                ('wins', models.IntegerField(blank=True, null=True)),
                ('loses', models.IntegerField(blank=True, null=True)),
                ('ties', models.IntegerField(blank=True, null=True)),
                ('race_count', models.IntegerField(blank=True, null=True)),
                ('last_played', models.IntegerField(blank=True, null=True)),
                ('current_win_streak', models.IntegerField(blank=True, null=True)),
                ('join_time', models.IntegerField(blank=True, null=True)),
                ('legacy_id', models.CharField(blank=True, max_length=45, null=True)),
                ('realm', models.IntegerField(blank=True, null=True)),
                ('path', models.CharField(blank=True, max_length=45, null=True)),
                ('clan_id', models.CharField(blank=True, db_column='Clan_id', max_length=45, null=True)),
                ('idblizz', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('mainrace', models.CharField(blank=True, max_length=45, null=True)),
                ('battletag', models.CharField(blank=True, db_column='Battletag', max_length=45, null=True)),
                ('offrace', models.IntegerField(blank=True, null=True)),
                ('league', models.IntegerField(blank=True, null=True)),
                ('lastmhupdate', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Players',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Progamer',
            fields=[
                ('idprogamer', models.AutoField(db_column='idProgamer', primary_key=True, serialize=False)),
                ('pseudo', models.CharField(blank=True, db_column='Pseudo', max_length=45, null=True)),
            ],
            options={
                'db_table': 'Progamer',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='players',
            name='smurf',
            field=models.ForeignKey(blank=True, db_column='smurf', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='starcraftHistory.Progamer'),
        ),
        migrations.AddField(
            model_name='games',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='starcraftHistory.Players'),
        ),
        migrations.AlterUniqueTogether(
            name='games',
            unique_together=set([('date', 'player')]),
        ),
    ]
