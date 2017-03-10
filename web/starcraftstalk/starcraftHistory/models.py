# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Games(models.Model):
    idgames = models.AutoField(db_column='idGames', primary_key=True)  # Field name made lowercase.
    path= models.CharField(max_length=45, blank=True, null=True)
    server = models.CharField(max_length=45, blank=True, null=True)
    player = models.ForeignKey('Players', models.DO_NOTHING, blank=True
    , null=True,related_name="games_as_p")
    map = models.CharField(max_length=45, blank=True, null=True)
    type = models.CharField(max_length=45, blank=True, null=True)
    decision = models.CharField(max_length=45, blank=True, null=True)
    speed = models.CharField(max_length=45, blank=True, null=True)
    date = models.IntegerField(blank=True, null=True)
    guessopid = models.ForeignKey('Players', models.DO_NOTHING, db_column='GuessOpId', blank=True,
     null=True,related_name="games_as_op")  # Field name made lowercase.

    #guessopgameid = models.IntegerField(db_column='GuessOpGameId', blank=True, null=True)  # Field name made lowercase.
    guessopgameid = models.ForeignKey('self',db_column='GuessOpGameId', blank=True, null=True)  # Field name made lowercase.

    current_mmr = models.CharField(db_column='Current_MMR', max_length=45, blank=True, null=True)  # Field name made lowercase.
    guessmmrchange = models.IntegerField(db_column='GuessMMRChange', blank=True, null=True)  # Field name made lowercase.
    current_rank = models.IntegerField(db_column='Current_Rank', blank=True, null=True)  # Field name made lowercase.

    #current_league = models.CharField(db_column='Current_league', max_length=45, blank=True, null=True)  # Field name made lowercase.
    current_league = models.ForeignKey('League',db_column='Current_league', max_length=45, blank=True, null=True)  # Field name made lowercase.

    current_win = models.IntegerField(db_column='Current_win', blank=True, null=True)  # Field name made lowercase.
    current_losses = models.IntegerField(db_column='Current_losses', blank=True, null=True)  # Field name made lowercase.
    current_ties = models.IntegerField(db_column='Current_ties', blank=True, null=True)  # Field name made lowercase.
    current_points = models.CharField(db_column='Current_Points', max_length=45, blank=True, null=True)  # Field name made lowercase.
    guessptschange = models.IntegerField(db_column='GuessPtsChange', blank=True, null=True)  # Field name made lowercase.
    ranked = models.CharField(max_length=10, blank=True, null=True)
    current_win_streak = models.IntegerField(blank=True, null=True)
    lastplayed_date = models.IntegerField(blank=True, null=True)
    total_season_games=models.IntegerField(blank=True, null=True)
    twins=models.IntegerField(blank=True, null=True)
    pwins=models.IntegerField(blank=True, null=True)
    zwins=models.IntegerField(blank=True, null=True)
    rankedwins=models.IntegerField(blank=True, null=True)
    rankedlosses=models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.idgames)
    class Meta:
        managed = True
        db_table = 'Games'
        unique_together = (('date', 'player'),)


class Players(models.Model):
    idplayer = models.AutoField(db_column='idPlayer', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45, blank=True, null=True)
    server = models.CharField(max_length=45, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(blank=True, null=True)
    loses = models.IntegerField(blank=True, null=True)
    ties = models.IntegerField(blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    race_count = models.IntegerField(blank=True, null=True)
    last_played = models.IntegerField(blank=True, null=True)
    current_win_streak = models.IntegerField(blank=True, null=True)
    join_time = models.IntegerField(blank=True, null=True)
    legacy_id = models.CharField(max_length=45, blank=True, null=True)
    realm = models.IntegerField(blank=True, null=True)
    path = models.CharField(max_length=45, blank=True, null=True)
    clan_id = models.CharField(db_column='Clan_id', max_length=45, blank=True, null=True)  # Field name made lowercase.
    idblizz = models.CharField(unique=True, max_length=20, blank=True, null=True)
    mainrace = models.CharField(max_length=45, blank=True, null=True)
    battletag = models.CharField(db_column='Battletag', max_length=45, blank=True, null=True)  # Field name made lowercase.
    smurf = models.ForeignKey('Progamer', models.DO_NOTHING, db_column='smurf', blank=True, null=True)
    offrace = models.IntegerField(blank=True, null=True)

    #league = models.IntegerField(blank=True, null=True)
    league = models.ForeignKey('League',blank=True, null=True)

    lastmhupdate = models.IntegerField(blank=True, null=True)
    alternate_path = models.CharField(max_length=45, blank=True, null=True)
    total_career_games=models.IntegerField(blank=True, null=True)
    total_season_games=models.IntegerField(blank=True, null=True)
    twins=models.IntegerField(blank=True, null=True)
    pwins=models.IntegerField(blank=True, null=True)
    zwins=models.IntegerField(blank=True, null=True)
    rankedwins=models.IntegerField(blank=True, null=True)
    rankedlosses=models.IntegerField(blank=True, null=True)



    class Meta:
        managed = True
        db_table = 'Players'

class League(models.Model):
	idleague=models.AutoField( primary_key=True)
	ladderid=models.IntegerField(blank=True, null=True)
	season=models.IntegerField(blank=True, null=True)
	level = models.IntegerField(blank=True, null=True)
	sigle = models.CharField(max_length=13,blank=True, null=True)
	server = models.CharField(max_length=2,blank=True, null=True)
	member_count = models.IntegerField(blank=True, null=True)

	def __str__(self):
		return str(self.ladderid)

class Progamer(models.Model):
    idprogamer = models.AutoField(db_column='idProgamer', primary_key=True)  # Field name made lowercase.
    pseudo = models.CharField(db_column='Pseudo', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Progamer'

class Global(models.Model):
    idglobal = models.AutoField(db_column='idglobal', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='name', max_length=45, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='value', max_length=45, blank=True, null=True)  # Field name made lowercase.
    def __str__(self):
        return str(self.name+" "+self.value)
    class Meta:
        managed = True
        db_table = 'Global'
class Clans(models.Model):
    idglobal = models.AutoField(db_column='idclans', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='name', max_length=45, blank=True, null=True)  # Field name made lowercase.
    abbrev = models.CharField(db_column='abbrev', max_length=45, blank=True, null=True)  # Field name made lowercase.
    idclan = models.IntegerField(db_column='idclan',  blank=True, null=True)  # Field name made lowercase.
    def __str__(self):
        return str(self.name)
    class Meta:
        managed = True
        db_table = 'Clans'
