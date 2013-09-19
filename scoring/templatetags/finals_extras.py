from django import template

register = template.Library()

def finals_block(bracket, args):
	if args is None:
		return ""

	arg_list = [arg.strip() for arg in args.split(',')]
	id1 = int(arg_list[0])
	id2 = int(arg_list[1])

	

	block = []

	

	block.append("<div class='match_number'>")
	if id1 == 1:
		block.append("Quarter ")
	elif id1 == 2:
		block.append("Semi-")

	block.append("Finals")
	block.append(" %d " % id2)
	block.append("</div>")

	if id1 in bracket and id2 in bracket[id1]:
		match = bracket[id1][id2][1]

		red_status = find_winner(bracket, id1, id2, 'Red')
		blue_status = find_winner(bracket, id1, id2, 'Blue')

		block.append("<div class='red'>")
		block.append("<div class='alliance'>Alliance %d </div>" % match.finals_red_alliance.number)
		block.append("<div class='teams'>Teams: %s </div>" % ','.join(match.red.team_numbers()))
		block.append("<div class='status'>%s</div>" % red_status)
		block.append("</div>")

		block.append("<div class='blue'>")
		block.append("<div class='alliance'>Alliance %d </div>" % match.finals_blue_alliance.number)
		block.append("<div class='teams'>Teams: %s </div>" % ','.join(match.blue.team_numbers()))
		block.append("<div class='status'>%s</div>" % blue_status)
		block.append("</div>")
	else:
		block.append("<div class='red'><div class='alliance'>Waiting for the winner from the previous match</div></div>")
		block.append("<div class='blue'><div class='alliance'>Waiting for the winner from the previous match</div></div>")


	return "\n".join(block)

def find_winner(bracket, id1, id2, side):
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
	if side == "Red":
		wins = red_wins
		other_wins = blue_wins
	else:
		wins = blue_wins
		other_wins = red_wins

	if wins >= 2:
		return "%s advances!" % side
	elif other_wins >= 2:
		return "%s played valiantly!" % side
	# elif red_wins + blue_wins + ties >= 1:
		# Checks if more than two matches have been played, but neither red nor blue won
		# Then we need another playoff match
		# We check if the last match is marked as played. 
		# This is an easy way to avoid duplicating a match.
		# if last_match.played:
			# next_match = next_finals_match(base_match_number, last_match)
			# base_match_number += 1
			# bracket_insert(bracket, next_match)

	return "%s needs %d win%s" % (side, (2 - wins), ("", "s")[(2 - wins) > 1])
	
register.filter('finals_block', finals_block)