import requests
import json
import datetime

def get_width(s):
	s = map(lambda x: len(x),s.split('\n'))
	return max(s)

class NSN:
	def __init__(self):
		self.url = 'https://tr.global.nba.com/stats2/scores/daily.json'
		self.json_raw = self.get_json_from_url(self.url)

	def get_json_from_url(self,url):
		return json.loads(requests.get(url).content)


	def extract_team_name(self,team):
		return team['profile']['abbr']

	def print_games(self,games):
		max_length = max(map(lambda x: get_width(x),games))
		result = ""
		sep = "*"*max_length
		result += sep + "\n"
		for game in games:
			result += game + "\n"
			result += sep + "\n"

		return result

	def get(self):	
		games = self.json_raw['payload']['date']['games']
		game_list = list()
		for game in games:
			home_name = self.extract_team_name(game['homeTeam'])
			home_score = game['boxscore']['homeScore']
			away_name = self.extract_team_name(game['awayTeam'])
			away_score = game['boxscore']['awayScore']

			game_list.append(tuple([home_name, str(home_score), away_name, str(away_score)]))


		return game_list


#nsn = NSN()
#print(nsn.get_before(1))
