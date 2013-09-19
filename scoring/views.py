from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.context_processors import csrf
from models import *
from forms import *


def calculate_rankings():
	#p = get_object_or_404(Poll, pk=poll_id)
	teams = Team.objects.all()
	matches = Match.objects.filter(played=True).filter(finals_match=False)

	rankings = {}
	for team in teams:
		rankings[team.number] = {
			'QS': 0,
			'sum_auto_goal': 0,
			'sum_climb_points': 0,
			'sum_teleop_points': 0, 
			'Wins': 0,
			'Losses': 0,
			'Ties': 0,
			'DQ': 0,
			'Played': 0
		}


	def add_win(rankings, match, team):
		rankings[team]['QS'] += 2
		rankings[team]['Wins'] += 1


	def add_loss(rankings, match, team):
		rankings[team]['Losses'] += 1

	def add_tie(rankings, match, team):
		rankings[team]['QS'] += 1
		rankings[team]['Ties'] += 1


	def add_all(rankings, match, scoring, team):
		rankings[team]['sum_auto_goal'] += scoring.score_hybrid()
		rankings[team]['sum_teleop_points'] += scoring.score_tele()
		rankings[team]['sum_climb_points'] += scoring.score_climb()

		rankings[team]['Played'] += 1


	def add_team_win(rankings, match, scoring):
		add_win(rankings, match, scoring.team1.number)
		add_win(rankings, match, scoring.team2.number)
		if scoring.team3:
			add_win(rankings, match, scoring.team3.number)

	def add_team_loss(rankings, match, scoring):
		add_loss(rankings, match, scoring.team1.number)
		add_loss(rankings, match, scoring.team2.number)
		if scoring.team3: 
			add_loss(rankings, match, scoring.team3.number)

	def add_team_tie(rankings, match, scoring):
		add_tie(rankings, match, scoring.team1.number)
		add_tie(rankings, match, scoring.team2.number)
		if scoring.team3: 
			add_tie(rankings, match, scoring.team3.number)

	

	for match in matches:
		# match.score()
		# print match.red_score, match.blue_score
		
		red = match.red
		blue = match.blue

		if match.red_score > match.blue_score:
			add_team_win(rankings, match, red)
			add_team_loss(rankings, match, blue)
		elif match.red_score < match.blue_score:
			add_team_loss(rankings, match, red)
			add_team_win(rankings, match, blue)
		else:
			add_team_tie(rankings, match, red)
			add_team_tie(rankings, match, blue)
		
		
		add_all(rankings, match, red, red.team1.number)
		add_all(rankings, match, red, red.team2.number)
		if red.team3: 
			add_all(rankings, match, red, red.team3.number)

		add_all(rankings, match, blue, blue.team1.number)
		add_all(rankings, match, blue, blue.team2.number)
		if blue.team3: 
			add_all(rankings, match, blue, blue.team3.number)

		# if red.coop and blue.coop:
		# 	rankings[red.team1.number]['CP'] += 2
		# 	rankings[red.team2.number]['CP'] += 2
		# 	if red.team3:
		# 		rankings[red.team3.number]['CP'] += 2
		# 	rankings[blue.team1.number]['CP'] += 2
		# 	rankings[blue.team2.number]['CP'] += 2
		# 	if blue.team3:
		# 		rankings[blue.team3.number]['CP'] += 2

		# 	rankings[red.team1.number]['QS'] += 2
		# 	rankings[red.team2.number]['QS'] += 2
		# 	if red.team3:
		# 		rankings[red.team3.number]['QS'] += 2
		# 	rankings[blue.team1.number]['QS'] += 2
		# 	rankings[blue.team2.number]['QS'] += 2
		# 	if blue.team3:
		# 		rankings[blue.team3.number]['QS'] += 2



	sorted_rankings = rankings.items()

	def sort_rankings(x, y):
		x = x[1]
		y = y[1]

		# print x, y

		if x['QS'] < y['QS']:
			return 1
		if x['QS'] > y['QS']:
			return -1

		if x['sum_auto_goal'] < y['sum_auto_goal']:
			return 1
		if x['sum_auto_goal'] > y['sum_auto_goal']:
			return -1

		if x['sum_climb_points'] < y['sum_climb_points']:
			return 1
		if x['sum_climb_points'] > y['sum_climb_points']:
			return -1

		if x['sum_teleop_points'] < y['sum_teleop_points']:
			return 1
		if x['sum_teleop_points'] > y['sum_teleop_points']:
			return -1

		return 0

	sorted_rankings.sort(cmp=sort_rankings)

	return sorted_rankings

def calculate_finals(initialize = False, show_next_matches = False):
	from django.db.models import Max
	from datetime import datetime

	alliances = Finals_Alliance.objects.all()
	if not alliances:
		return None

	finals_matches = Match.objects.filter(finals_match = True)

	bracket = dict()

	base_match_number = int(Match.objects.all().aggregate(Max('number'))['number__max'] or 0) + 1


	def bracket_insert(bracket, match):
		if match.finals_id_1 not in bracket:
			bracket[match.finals_id_1] = dict()

		if match.finals_id_2 not in bracket[match.finals_id_1]:
			bracket[match.finals_id_1][match.finals_id_2] = dict()

		bracket[match.finals_id_1][match.finals_id_2][match.finals_id_3] = match
	
	def next_finals_match(number, match):
		return construct_finals_match(number, match.finals_red_alliance.number, match.finals_blue_alliance.number, match.finals_id_1, match.finals_id_2, match.finals_id_3 + 1, True)

	def construct_finals_match(number, red_num, blue_num, id1, id2, id3, save = False):
		match = Match()

		match.number = number

		match.time = datetime.now()
				
		match.finals_match = True

		match.finals_id_1 = id1
		match.finals_id_2 = id2
		match.finals_id_3 = id3


		red = Scoring()
		red_alliance = Finals_Alliance.objects.get(number = red_num)
		red.team1 = red_alliance.team1
		red.team2 = red_alliance.team2
		red.team3 = red_alliance.team3
		match.finals_red_alliance = red_alliance

		blue = Scoring()
		blue_alliance = Finals_Alliance.objects.get(number = blue_num)
		blue.team1 = blue_alliance.team1
		blue.team2 = blue_alliance.team2
		blue.team3 = blue_alliance.team3
		match.finals_blue_alliance = blue_alliance

		if save:
			red.save()
			blue.save()

		match.red = red
		match.blue = blue

		if save:
			match.save()

		return match

	def find_winner(id1, id2, base_match_number):
		# Tally up the number of wins on each side
		red_wins = 0
		blue_wins = 0
		ties = 0

		for fid3num, match in bracket[id1][id2].items():
			if not match.played:
				continue
			
			if match.red_score > match.blue_score:
				red_wins += 1
			elif match.red_score < match.blue_score:
				blue_wins += 1
			else:
				ties += 1


		last_match = bracket[id1][id2][len(bracket[id1][id2])]

		# Figure out who advances
		if red_wins >= 2:
			# Red advances
			return last_match.finals_red_alliance
		elif blue_wins >= 2:
			# Blue advances
			return last_match.finals_blue_alliance
		elif red_wins + blue_wins + ties >= 1:
			# Checks if more than two matches have been played, but neither red nor blue won
			# Then we need another playoff match
			# We check if the last match is marked as played. 
			# This is an easy way to avoid duplicating a match.
			if last_match.played:
				next_match = next_finals_match(base_match_number, last_match)
				base_match_number += 1
				bracket_insert(bracket, next_match)
			return None

	# Populate the bracket with the existing matches
	for match in finals_matches:
		bracket_insert(bracket, match)

	# Used to populate the bracket with the first batch of quarter final matches
	if initialize:
		# Sets up the first two matches
		for match_number in range(1,2):
			for x in range(1,5):
				match = construct_finals_match(base_match_number, x, (8-(x-1)), 1, x, match_number, True)
				base_match_number += 1
				bracket_insert(bracket, match)

	# Next we need to figure out placeholder matches
	if show_next_matches and 1 in bracket:

		

		quarter_winners = dict()

		quarter_winners[1] = find_winner(1,1, base_match_number)
		quarter_winners[2] = find_winner(1,2, base_match_number)
		quarter_winners[3] = find_winner(1,3, base_match_number)
		quarter_winners[4] = find_winner(1,4, base_match_number)

		if quarter_winners[1] and quarter_winners[4] and (2 not in bracket or 1 not in bracket[2]):
			match = construct_finals_match(base_match_number, quarter_winners[1].number, quarter_winners[4].number, 2, 1, 1, True)
			base_match_number += 1
			bracket_insert(bracket, match)

		if quarter_winners[2] and quarter_winners[3] and (2 not in bracket or 2 not in bracket[2]):
			match = construct_finals_match(base_match_number, quarter_winners[2].number, quarter_winners[3].number, 2, 2, 1, True)
			base_match_number += 1
			bracket_insert(bracket, match)

		
		# Next, if both semi final matches are in, we can figure out the winner
		if 2 in bracket:
			semi_winners = dict()
			if 1 in bracket[2]:
				semi_winners[1] = find_winner(2,1, base_match_number)
			if 2 in bracket[2]:
				semi_winners[2] = find_winner(2,2, base_match_number)

			# Make the first finals match if necessary
			if 1 in semi_winners and semi_winners[1] and 2 in semi_winners and semi_winners[2]:
				print "I have semi winners", semi_winners

				if 3 not in bracket or 1 not in bracket[3]:
					match = construct_finals_match(base_match_number, semi_winners[1].number, semi_winners[2].number, 3, 1, 1, True)
					base_match_number += 1
					bracket_insert(bracket, match)

				# Run find winner to possibly make more matches as needed
				if 1 in bracket[3]:
					find_winner(3,1, base_match_number)


					
	




	# print bracket
	return bracket


def rankings(request):
	rankings = calculate_rankings()
	return render_to_response('rankings.html', {"rankings": rankings})

def rankings_print(request):
	rankings = calculate_rankings()
	return render_to_response('rankings_print.html', {"rankings": rankings})

def matchlist(request):
	matchlist = Match.objects.filter(finals_match = False)
	finals_bracket = calculate_finals(initialize = False, show_next_matches = True)
	return render_to_response('matchlist.html', {"matchlist": matchlist, "bracket": finals_bracket})

def matchlist_print(request):
	matchlist = Match.objects.filter(finals_match = False)
	return render_to_response('matchlist_print.html', {"matchlist": matchlist})

def first_matchlist(request):
	matchlist = Match.objects.filter(finals_match = False)
	finals_bracket = calculate_finals(initialize = False, show_next_matches = True)
	highest_played_match = 0
	for match in matchlist:
		if match.played:
			highest_played_match = match.number

	return render_to_response('first_format_matchlist.html', {"matchlist": matchlist, "bracket": finals_bracket, "highest_played_match": highest_played_match})

def first_rankings(request):
	rankings = calculate_rankings()
	return render_to_response('first_format_rankings.html', {"rankings": rankings})

def finals_bracket(request):
	bracket = calculate_finals()
	return render_to_response('finals_bracket.html', {"bracket": bracket})

def json_rankings(request):
	import json
	# from django.forms import model_to_dict
	rankings = calculate_rankings()

	return HttpResponse(json.dumps(rankings), mimetype="application/json")

def json_matchlist(request):
	import json
	from django.forms import model_to_dict
	matchlist = Match.objects.filter(finals_match = False)

	dict_list = []
	for match in matchlist:
		dict_match = model_to_dict(match)
		dict_match['red'] = model_to_dict(match.red)
		dict_match['blue'] = model_to_dict(match.blue)
		dict_list.append(dict_match)

	# http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
	def handler(obj):
		if hasattr(obj, 'isoformat'):
			return obj.isoformat()
		return obj
	return HttpResponse(json.dumps(dict_list, default=handler), mimetype="application/json")

def tv_display(request):
	return render_to_response('tv_display.html')

def edit_team(request):
	pass

def admin(request):
	# rankings = calculate_rankings()
	return render_to_response('admin.html')

def edit_match(request, matchid):
	c = {}
	c.update(csrf(request))

	match = get_object_or_404(Match, pk=matchid)

	if request.method == 'POST': 

		match.blue.penalties = int(request.POST['blue_penalties'])
		match.red.penalties = int(request.POST['red_penalties'])

		if 'played' in request.POST and request.POST['played'] == "True":
			match.played = True
		else:
			match.played = False

		# match.red_score = match.red.score()
		# match.blue_score = match.blue.score()
		match.score()
		
		match.blue.save()
		match.red.save()
		match.save()

		c['saved'] = True
	# 	form = MatchForm(request.POST, request.FILES)
	# 	if form.is_valid(): 
	# 		match = form.save(commit=False)
	# 		match.save()

	# 		return render_to_response('edit_match.html', {'success': True, 'form': form, 'blockform': True}, context_instance=RequestContext(request))
	# else:
	# 	if matchid == None:
	# 		form = MatchForm()
	# 	else:
	# 		match = Match.objects.get(pk=matchid)
	# 		form = MatchForm(instance=match)

	# return render_to_response('edit_match.html', {'form': form}, context_instance=RequestContext(request))

	
	c['match'] = match
	return render_to_response('edit_match.html', c)


def edit_match_scoring(request, matchid, side):
	c = {}
	c.update(csrf(request))
	matchid = int(matchid)
	match = get_object_or_404(Match, pk=matchid)

	if side == 'blue':
		scores = match.blue
		c['side'] = 'blue'
		c['otherside'] = 'red'
	elif side == 'red':
		scores = match.red
		c['side'] = 'red'
		c['otherside'] = 'blue'

	if request.method == 'POST': 
		scores.hybrid_top = int(request.POST['hybrid_top'])
		scores.hybrid_mid = int(request.POST['hybrid_midl']) + int(request.POST['hybrid_midr'])
		scores.hybrid_low = int(request.POST['hybrid_low'])

		scores.tele_top = int(request.POST['tele_top'])
		scores.tele_mid = int(request.POST['tele_midl']) + int(request.POST['tele_midr'])
		scores.tele_low = int(request.POST['tele_low'])

		scores.tele_pyramid = int(request.POST['tele_pyramid'])

		scores.pyramid_level1 = int(request.POST['pyramid_level1'])
		scores.pyramid_level2 = int(request.POST['pyramid_level2'])
		scores.pyramid_level3 = int(request.POST['pyramid_level3'])

		scores.submitted = True

		scores.save()
		c['saved'] = True

	if Match.objects.filter(number=matchid+1).exists():
		c['nextmatch'] = matchid + 1
	if Match.objects.filter(number=matchid-1).exists():
		c['prevmatch'] = matchid - 1
	
	c['currentmatch'] = match
	c['played'] = match.played
	c['scores'] = scores

	return render_to_response('edit_match_scoring.html', c)

def view_match_scoring_json(request, matchid, side):
	import json
	from django.forms import model_to_dict
	match = get_object_or_404(Match, pk=matchid)

	if side == "red":
		scores =  match.red
	if side == "blue":
		scores = match.blue

	if scores:
		dict_scores = model_to_dict(scores)
		dict_scores['played'] = match.played
		dict_scores['score'] = scores.score();
		return HttpResponse(json.dumps(dict_scores), mimetype="application/json")
	
	return HttpResponse(json.dumps("Error!"), mimetype="application/json")

def matchlist_generate(request):
	import subprocess
	import os

	try:
		root_path = os.path.dirname(os.path.realpath(__file__))

		match_maker_path = os.path.join(root_path, '../matchmaker/MatchMaker')
		match_rater_path = os.path.join(root_path, '../matchmaker/MatchRater')
		team_list_path = os.path.join(root_path,'../matchmaker/team_list.txt')
		match_list_path = os.path.join(root_path,'../matchmaker/match_list_gen.txt')

		teams = Team.objects.all()

		team_list = open(team_list_path, 'w')

		for team in teams:
			team_list.write("%d\n" % team.number)

		team_list.close()

		# output = os.system(' '.join((path, '-t', '20' '-r', '6')))

		output = subprocess.check_output([match_maker_path, '-l', team_list_path, '-r', '6', '-s', '-b'])
		

		match_list = open(match_list_path, 'w')
		match_list.write(output)
		match_list.close()
		

		rater_output = subprocess.check_output([match_rater_path, '-s', match_list_path])

	except subprocess.CalledProcessError, e:
		# print subprocess.CalledProcessError
		output = e.output
		rater_output = ""

	return render_to_response('matchlist_generate.html', {"output": output, "rater_output": rater_output})


def matchlist_import(request):
	c = {}
	c.update(csrf(request))

	import os
	from datetime import datetime

	root_path = os.path.dirname(os.path.realpath(__file__))
	match_list_path = os.path.join(root_path,'../matchmaker/match_list_gen.txt')

	match_list_raw = open(match_list_path, 'r')

	matchlist = []

	
	for match_raw in match_list_raw:
		match_split = match_raw.split(' ')
		if len(match_split) <= 1:
			continue
		
		match = Match()
		match.number = int(match_split[0])
		red = Scoring()
		# print int(match_split[1])
		red.team1 = Team.objects.get(number=int(match_split[1]))
		red.team2 = Team.objects.get(number=int(match_split[3]))
		red.team3 = Team.objects.get(number=int(match_split[5]))

		blue = Scoring()

		blue.team1 = Team.objects.get(number=int(match_split[7]))
		blue.team2 = Team.objects.get(number=int(match_split[9]))
		blue.team3 = Team.objects.get(number=int(match_split[11]))

		

		match.finals_match = False
		
		if request.method == 'POST':
			# match.time = 
			match.time = datetime.strptime(request.POST['m%dtime' % match.number], "%m/%d/%Y %H:%M")
			
			blue.save()
			red.save()

			match.blue = blue
			match.red = red
			match.save()

		match.blue = blue
		match.red = red

		matchlist.append(match)

	c['matchlist'] = matchlist

	return render_to_response('matchlist_import.html', c)

def edit_alliances(request):
	from time import localtime, strftime
	c = {}
	c.update(csrf(request))

	alliances = Finals_Alliance.objects.all()
	rankings = calculate_rankings()

	alliance_list = []

	if len(alliances) == 0:
		# need to make a bunch
		i = 1
		for team, scores in rankings:
			if i > 8:
				break

			alliance = Finals_Alliance()
			alliance.number = i
			alliance.team1 = Team.objects.get(number=int(team))
			alliance_list.append(alliance)

			i += 1
	else:
		alliance_list = alliances


	if request.method == 'POST':
		if 'save_alliances' in request.POST:
			for alliance in alliance_list:
				alliance.team1 = Team.objects.get(number=int(request.POST['a%dt1' % alliance.number])) if 'a%dt1' % alliance.number in request.POST else None
				alliance.team2 = Team.objects.get(number=int(request.POST['a%dt2' % alliance.number])) if 'a%dt2' % alliance.number in request.POST else None
				alliance.team3 = Team.objects.get(number=int(request.POST['a%dt3' % alliance.number])) if 'a%dt3' % alliance.number in request.POST else None
				alliance.team4 = Team.objects.get(number=int(request.POST['a%dt4' % alliance.number])) if 'a%dt4' % alliance.number in request.POST else None
				alliance.save()
			c['saved'] = True
		if 'generate_finals' in request.POST:
			bracket = calculate_finals(initialize=True, show_next_matches=False)
			c['saved'] = True
	else:
		c['saved'] = False

	c['rankings'] = rankings
	c['alliances'] = alliance_list
	c['time'] = strftime("%I:%M:%S %p", localtime())
	return render_to_response('edit_alliances.html', c)


def homepage(request):
	steps = dict()

	teams = Team.objects.all()
	if len(teams) > 0:
		steps[1] = "complete"
	else:
		steps[1] = "current"
	
	matches = Match.objects.all().filter(finals_match = False)
	matches_played = Match.objects.all().filter(finals_match = False).filter(played = True)
	finals_alliances = Finals_Alliance.objects.all()
	finals_matches = Match.objects.all().filter(finals_match = True)

	if len(matches) > 0:
		steps[2] = "complete"
	elif steps[1] == "current":
		steps[2] = "todo"
	else:
		steps[2] = "current"

	
	if len(matches) == len(matches_played):
		steps[3] = "complete"
	elif len(matches) > 0:
		steps[3] = "current"
	else:
		steps[3] = "todo"

	

	if len(finals_alliances) > 0 and len(finals_matches) >= 4:
		steps[4] = "complete"
	else:
		steps[4] = "todo"


	# matchlist = Match.objects.all()
	return render_to_response('home.html', {"steps": steps})
	# return matchlist(request)