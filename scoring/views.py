from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.context_processors import csrf
from models import *
from forms import *


def calculate_rankings():
	# TODO: Add coopertition points to the QP
	
	#p = get_object_or_404(Poll, pk=poll_id)
	teams = Team.objects.all()
	matches = Match.objects.all()

	rankings = {}
	for team in teams:
		rankings[team.number] = {
			'QS': 0,
			'HP': 0,
			'BP': 0,
			'TP': 0,
			'CP': 0,
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
		rankings[team]['HP'] += scoring.score_hybrid()
		rankings[team]['TP'] += scoring.score_tele()
		rankings[team]['Played'] += 1
		if scoring.coop:
			rankings[team]['QS'] += 2

	def add_team_win(rankings, match, scoring):
		add_win(rankings, match, scoring.team1.number)
		add_win(rankings, match, scoring.team2.number)
		add_win(rankings, match, scoring.team3.number)

	def add_team_loss(rankings, match, scoring):
		add_loss(rankings, match, scoring.team1.number)
		add_loss(rankings, match, scoring.team2.number)
		add_loss(rankings, match, scoring.team3.number)

	def add_team_tie(rankings, match, scoring):
		add_tie(rankings, match, scoring.team1.number)
		add_tie(rankings, match, scoring.team2.number)
		add_tie(rankings, match, scoring.team3.number)

	

	for match in matches:
		match.score()
		print match.red_score, match.blue_score
		
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
		add_all(rankings, match, red, red.team3.number)

		add_all(rankings, match, blue, blue.team1.number)
		add_all(rankings, match, blue, blue.team2.number)
		add_all(rankings, match, blue, blue.team3.number)

	sorted_rankings = rankings.items()

	def sort_rankings(x, y):
		x = x[1]
		y = y[1]

		print x, y

		if x['QS'] < y['QS']:
			return 1
		if x['QS'] > y['QS']:
			return -1

		if x['HP'] < y['HP']:
			return 1
		if x['HP'] > y['HP']:
			return -1

		if x['BP'] < y['BP']:
			return 1
		if x['BP'] > y['BP']:
			return -1

		if x['TP'] < y['TP']:
			return 1
		if x['TP'] > y['TP']:
			return -1

		return 0

	sorted_rankings.sort(cmp=sort_rankings)
	print sorted_rankings

	return sorted_rankings
	#return render_to_response('rankings.html', {"rankings": teams})

def rankings(request):
	rankings = calculate_rankings()
	return render_to_response('rankings.html', {"rankings": rankings})

def matchlist(request):
	matchlist = Match.objects.all()
	return render_to_response('matchlist.html', {"matchlist": matchlist})

def edit_team(request):
	pass

def edit_match(request, matchid):
	if request.method == 'POST': 
		form = MatchForm(request.POST, request.FILES)
		if form.is_valid(): 
			match = form.save(commit=False)
			match.save()

			return render_to_response('edit_match.html', {'success': True, 'form': form, 'blockform': True}, context_instance=RequestContext(request))
	else:
		if matchid == None:
			form = MatchForm()
		else:
			match = Match.objects.get(pk=matchid)
			form = MatchForm(instance=match)

	return render_to_response('edit_match.html', {'form': form}, context_instance=RequestContext(request))

	match = get_object_or_404(Match, pk=match)
	return render_to_response('edit_match.html', {"match": match})

def edit_match_scoring(request, matchid, side):
	return render_to_response('edit_match_scoring.html')

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

		output = subprocess.check_output([match_maker_path, '-l', team_list_path, '-r', '6', '-s'])
		

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

def homepage(request):
	return render_to_response('home.html')