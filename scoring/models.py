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

	finals_red_alliance = models.ForeignKey('Finals_Alliance', related_name='+', blank = True, null=True)
	finals_blue_alliance = models.ForeignKey('Finals_Alliance', related_name='+', blank = True, null=True)

	updated = models.DateTimeField(auto_now=True, null=True)

	def __unicode__(self):
		if self.finals_match:
			return "Match %d - %s Finals %d match %d" % (self.number, ("", "Quarter", "Semi", "")[self.finals_id_1], self.finals_id_2, self.finals_id_3)
		return "Match %d" % self.number
	
	def score(self):
		self.red_score = self.red.score() + self.blue.penalties
		self.blue_score = self.blue.score() + self.red.penalties
		# self.save()

class Scoring(models.Model):
	team1 = models.ForeignKey('Team', related_name='+')
	team2 = models.ForeignKey('Team', related_name='+', blank = True, null=True)
	team3 = models.ForeignKey('Team', related_name='+', blank = True, null=True)

	hybrid_top = models.IntegerField(default = 0)
	hybrid_mid = models.IntegerField(default = 0)
	hybrid_low = models.IntegerField(default = 0)

	tele_top = models.IntegerField(default = 0)
	tele_mid = models.IntegerField(default = 0)
	tele_low = models.IntegerField(default = 0)
	tele_pyramid = models.IntegerField(default = 0)

	pyramid_options = (
		(0, "No bots at this level"),
		(1, "One bot at this level"),
		(2, "Two bots at this level"),
		(3, "Three bots at this level")
	)

	pyramid_level1 = models.IntegerField(choices=pyramid_options, default = 0)
	pyramid_level2 = models.IntegerField(choices=pyramid_options, default = 0)
	pyramid_level3 = models.IntegerField(choices=pyramid_options, default = 0)

	# coop = models.BooleanField(default = False)

	# final_red_ball = models.IntegerField(default = 0)

	team1_disqualified = models.BooleanField(default = False)
	team2_disqualified = models.BooleanField(default = False)
	team3_disqualified = models.BooleanField(default = False)

	penalties = models.IntegerField(default = 0)

	updated = models.DateTimeField(auto_now=True, null=True)

	submitted = models.BooleanField(default = False)

	def score_hybrid(self):
		return self.hybrid_top*6 + self.hybrid_mid*4 + self.hybrid_low*2

	def score_tele(self):
		return self.tele_top*3 + self.tele_mid*2 + self.tele_low + self.tele_pyramid*5

	def score_climb(self):
		
		climb_points = self.pyramid_level1 * 10 + self.pyramid_level2 * 20 + self.pyramid_level3 * 30

		return climb_points

	def score(self):
		score = 0

		score += self.score_hybrid()
		score += self.score_tele()
		score += self.score_climb()

		# score -= self.penalties

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

	def team_numbers(self):
		# returns a list of the team numbers
		list = ["%d" % self.team1.number]
		if self.team2:
			list.append("%d" % self.team2.number)
		if self.team3:
			list.append("%d" % self.team3.number)
		return list



class Finals_Alliance(models.Model):
	number = models.IntegerField(primary_key=True)

	team1 = models.ForeignKey('Team', related_name='+')
	team2 = models.ForeignKey('Team', related_name='+', blank = True, null=True)
	team3 = models.ForeignKey('Team', related_name='+', blank = True, null=True)
	team4 = models.ForeignKey('Team', related_name='+', blank = True, null=True)

	updated = models.DateTimeField(auto_now=True, null=True)

	def __unicode__(self):
		return "Finals Alliance %d" % self.number
