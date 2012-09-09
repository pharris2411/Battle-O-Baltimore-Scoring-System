from django.db import models


class Team(models.Model):
	number = models.IntegerField(unique = True, primary_key=True)
	name = models.CharField(max_length=200, blank = True)
	sponsors = models.CharField(max_length=400, blank = True)
	
	yellowcard = models.BooleanField(default = False)
	redcard = models.BooleanField(default = False)

	updated = models.DateTimeField(auto_now=True, null=True)

	def __unicode__(self):
		return "%d - %s" % (self.number, self.name)

class Match(models.Model):
	number = models.IntegerField(primary_key=True)

	time = models.DateTimeField()

	red_score = models.IntegerField(default = 0)
	blue_score = models.IntegerField(default = 0)

	red = models.ForeignKey('Scoring', related_name='red_alliance_match', on_delete=models.CASCADE)
	blue = models.ForeignKey('Scoring', related_name='blue_alliance_match', on_delete=models.CASCADE)

	played = models.BooleanField(default = False)

	finals_match = models.BooleanField(default = False)

	finals_id_1 = models.IntegerField(default=0, blank=True)
	finals_id_2 = models.IntegerField(default=0, blank=True)
	finals_id_3 = models.IntegerField(default=0, blank=True)

	updated = models.DateTimeField(auto_now=True, null=True)

	def __unicode__(self):
		return "Match %d" % self.number
	
	def score(self):
		self.red_score = self.red.score()
		self.blue_score = self.blue.score()

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

	final_red_ball = models.IntegerField(default = 0)

	team1_disqualified = models.BooleanField(default = False)
	team2_disqualified = models.BooleanField(default = False)
	team3_disqualified = models.BooleanField(default = False)

	penalties = models.IntegerField(default = 0)

	updated = models.DateTimeField(auto_now=True, null=True)

	def score_hybrid(self):
		return self.hybrid_top*6 + self.hybrid_mid*5 + self.hybrid_low*4

	def score_tele(self):
		return self.tele_top*3 + self.tele_mid*2 + self.tele_low

	def score(self):
		score = 0

		score += self.score_hybrid()
		score += self.score_tele()
		
		# max of 20 points 
		bridge_points = self.bridge * 10
		if(bridge_points > 20):
			bridge_points = 20
		score += bridge_points

		score += (self.final_red_ball * 20)
		score -= self.penalties

		return score

	def __unicode__(self):
		# hacky solution, but it works.
		match_red = Match.objects.filter(red = self.id)
		if match_red:
			return "Scores for match %d - red" % match_red[0].number
		
		match_blue = Match.objects.filter(blue = self.id)
		if match_blue:
			return "Scores for match %d - blue" % match_blue[0].number

		return "Scores - associated match not found?"



class Finals_Alliance(models.Model):
	number = models.IntegerField(primary_key=True)

	team1 = models.ForeignKey('Team', related_name='+')
	team2 = models.ForeignKey('Team', related_name='+', blank = True, null=True)
	team3 = models.ForeignKey('Team', related_name='+', blank = True, null=True)
	team4 = models.ForeignKey('Team', related_name='+', blank = True, null=True)

	updated = models.DateTimeField(auto_now=True, null=True)

	def __unicode__(self):
		return "Finals Alliance %d" % self.number
