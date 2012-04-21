from django.db import models


class Team(models.Model):
	number = models.IntegerField(unique = True)
	name = models.CharField(max_length=200, blank = True)
	sponsors = models.CharField(max_length=400, blank = True)
	
	yellowcard = models.BooleanField(default = False)
	redcard = models.BooleanField(default = False)

	def __unicode__(self):
		return "%d - %s" % (self.number, self.name)

class Match(models.Model):
	number = models.IntegerField()

	time = models.DateTimeField()

	red_score = models.IntegerField(default = 0)
	blue_score = models.IntegerField(default = 0)

	red = models.ForeignKey('Scoring', related_name='red_alliance_match')
	blue = models.ForeignKey('Scoring', related_name='blue_alliance_match')

	played = models.BooleanField(default = False)

	def __unicode__(self):
		return "Match %d" % self.number
	

class Scoring(models.Model):
	team1 = models.ForeignKey('Team', related_name='+')
	team2 = models.ForeignKey('Team', related_name='+', blank = True)
	team3 = models.ForeignKey('Team', related_name='+', blank = True)

	hybrid_top = models.IntegerField(default = 0)
	hybrid_mid = models.IntegerField(default = 0)
	hybrid_low = models.IntegerField(default = 0)

	tele_top = models.IntegerField(default = 0)
	tele_mid = models.IntegerField(default = 0)
	tele_low = models.IntegerField(default = 0)

	bridge_options = (
		(0, "No bots balanced"),
		(1, "One bot balanced"),
		(2, "Two bots balanced"),
		(3, "Three bots balanced")
	)

	bridge = models.IntegerField(choices=bridge_options, default = 0)

	coop = models.BooleanField(default = False)

	team1_disqualified = models.BooleanField(default = False)
	team2_disqualified = models.BooleanField(default = False)
	team3_disqualified = models.BooleanField(default = False)

	penalties = models.IntegerField(default = 0)
