from flask import Flask, Response, render_template, url_for, request, jsonify
import time, math, random
import json
import random
from datetime import datetime
from datetime import date 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pickle
from bs4 import BeautifulSoup
import numpy as np
from apscheduler.scheduler import Scheduler
import atexit
import requests
import hashlib
from flask_script import Manager, Server
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
ENV = 'prod'
if ENV == 'dev':
    app.debug = True 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Qwertyu7@localhost:5430/match_predictions_db'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://laceytptczrvpl:f6ff6a957921c789abc9fbe331e5fe1b4d0a88343511bcb38ad86f5e997ed706@ec2-54-147-209-121.compute-1.amazonaws.com:5432/dnr9intjchd5a'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MatchPredictions(db.Model):
    _tablename_ = 'Match Predictions'
    match_id = db.Column(db.BigInteger, primary_key = True)
    match_date = db.Column(db.String(100))
    team1_name = db.Column(db.String(100))
    team2_name = db.Column(db.String(100))
    match_link = db.Column(db.String(100))
    team1_win  =  db.Column(db.Integer)
    team1_probability  =  db.Column(db.Float)
    team2_probability =  db.Column(db.Float)
    team1_won  =  db.Column(db.Integer)
    team1_coeff = db.Column(db.Float)
    team2_coeff = db.Column(db.Float)

    def __init__(self, match_id, match_date, team1_name, team2_name, 
                match_link, team1_win, team1_probability, team2_probability, team1_won, team1_coeff, team2_coeff):
                self.match_id = match_id
                self.match_date = match_date
                self.team1_name = team1_name
                self.team2_name = team2_name
                self.match_link = match_link
                self.team1_win = team1_win
                self.team1_probability = team1_probability
                self.team2_probability = team2_probability
                self.team1_won = team1_won
                self.team1_coeff = team1_coeff
                self.team2_coeff = team2_coeff

class UpcomingMatches(db.Model):
    _tablename_ = 'Upcoming Matches'
    match_id = db.Column(db.BigInteger, primary_key = True)
    match_date = db.Column(db.String(100))
    team1_name = db.Column(db.String(100))
    team2_name = db.Column(db.String(100))
    match_link = db.Column(db.String(100))

    def __init__(self, match_id, match_date, team1_name, team2_name, 
                match_link):
                self.match_id = match_id
                self.match_date = match_date
                self.team1_name = team1_name
                self.team2_name = team2_name
                self.match_link = match_link

matches_list = [
    {
        "team1_name": "NiP",
        "team2_name": "FaZe",
        "match_date": "01.23.2019 4:00 ETC",
        "match_link": "test.com"
    },
    {
        "team1_name": "BIG",
        "team2_name": "OG",
        "match_date": "11.23.2019 4:00 ETC",
        "match_link": "test.com"
    },
]
matches_discarded = []
team_stats = {}
import datetime
date_started = datetime.datetime.now()
TEAMS = {
#   "Na'Vi": "4608/natus-vincere",
 # "Fnatic": "4991/fnatic",
#   "Astralis": "6665/astralis",
#   "mousesports" : "4494/mousesports", 
 # "G2" : "5995/g2",
 # "Liquid" : "5973/liquid",
 # "EG" : "10399/evil-geniuses",
  "FaZe" : "6667/faze",
 # "100 Thieves" : "8474/100-thieves",
  "NiP" : "4411/nip",
  "OG" : "10503/og",
  "BIG" : "7532/big",
 # "mibr" : "9215/mibr",
  # "Ence" : "4869/ence",
  #"Godsent" : "6902/godsent",
    # "Renegades" : "6211/renegades",
  #  "Cloud9" : "5752/cloud9",
  #  "Sprout" : "8637/sprout",
  #  "Vitality" : "9565/vitality",
    # "pro100" : "7898/pro100",
   # "Heretics" : "8346/heretics",
    # "coL" : "5005/complexity",
  #  "forZe" : "8135/forze",
  #  "FURIA" : "8297/furia",
  #  "Spirit" : "7020/spirit",
  #"North" : "7533/north",
#   "HAVU" : 7865/havu",
  #  "VP" : "5378/virtuspro",
    # "MAD Lions" : "8362/mad-lions"
 #"Gen.G" : "10514/geng",
#  'Winstrike': '9183/winstrike',
# 'c0ntact': '10606/c0ntact',
 # 'Heroic': '7175/heroic',
  # 'Secret': '10488/secret',
 # "Espada": '8669/espada',
 # 'Hard Legion': "10421/hard-legion",
 # 'Syman': '8772/syman',
 # "ALTERNATE aTTaX": '4501/alternate-attax',
 # "SG.pro": '10105/sgpro'
}


with open(f'CSGOmodel.pkl', 'rb') as f:
    model = pickle.load(f)

cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()

# @app.route("/api/matches", methods=["GET", "POST"])
# def api_matches():
#     if(request.method == 'POST'): 
#         matches_json = request.get_json()
#         global matches_list
#         del matches_list[:]
#         for match_json in matches_json:
#             contains1 = False
#             contains2 = False
#             for key in TEAMS:
#                 if matches_json.get(match_json)[2].replace(" ", "")  == key.replace(" ", ""):
#                     contains1 = True
#                 if matches_json.get(match_json)[3].replace(" ", "")  == key.replace(" ", ""):
#                     contains2 = True
#             if (contains1 and contains2):
#                 # add to list of matches (global var)
#                 matches_list.append(matches_json.get(match_json))
#                 # predict result and store in the database
#                 time_fixed_str = matches_json.get(match_json)[1]
#                 team1_str = matches_json.get(match_json)[2]
#                 team2_str = matches_json.get(match_json)[3]
#                 match_link = matches_json.get(match_json)[6].strip()
#                 match_id = ''.join(letter for letter in match_link if letter.isdigit())
#                 # #check if match has been predicted in the database
#                 # if db.session.query(MatchPredictions).filter(MatchPredictions.match_id == match_id).count() == 0:
#                 #         response = requests.get('https://csgopredict.herokuapp.com/api/predict' + '?team1=' + team1_str.strip() + '&team2=' + team2_str.strip())
#                 #         response = response.json()
#                 #         prediction = MatchPredictions(match_id, time_fixed_str, team1_str, team2_str,
#                 #                             match_link, response.get("Team1_Predicted_Win"), response.get("Probability_1"), response.get("Probability_2"), -1, 0.0 ,0.0)
#                 #         db.session.add(prediction)
#                 #         db.session.commit()
#                 #         #handle exception (model not loaded)
#             else:
#                 global matches_discarded
#                 matches_discarded.append(matches_json.get(match_json)[2] + ' ' + matches_json.get(match_json)[3])
#             # removing old matches that are not in new list
#             # for match_in_temp in matches_list_temp:
#             #     found = False
#             #     for match_in_list in matches_list:
#             #         while (not found):
#             #             if (match_in_list == match_in_temp):
#             #                 matches_list.remove(match_in_list)
#             #                 found = True
#             #     matches_list.append(match_in_temp)
#         return jsonify(matches_json)

@app.route("/api/model",  methods=["GET", "POST"])
def api_teamstats():
    coeff = model[0].coef_
    return str(coeff)

@app.route("/api/predict", methods=["GET"])
def predict():
    if (request.method == 'GET'):
        team1_name = request.args.get('team1')
        team2_name = request.args.get('team2')
        team1_stats = team_stats.get(team1_name)
        team2_stats = team_stats.get(team2_name)
        stats_diff = np.subtract(team1_stats,team2_stats)
        team1_predicted_win = int(model[0].predict([stats_diff])[0])
        # return str('difference between ' + team1_name + " and "  + team2_name + ' is ' + str(stats_diff))
        coeff = model[0].coef_[0]
        S = 0; 
        for i in range(0,len(coeff)):
            S = S + coeff[i]*stats_diff[i]
        probability = 1/(1+ np.exp(-S))
        if team1_predicted_win == 0:
            prediction_team = team2_name
            probability_2 = 1 - probability
            probability_1 = probability
        else:
            prediction_team = team1_name
            probability_1 = probability
            probability_2 = 1 - probability
        message = {
            "Prediction_Teamname" : prediction_team,
            "Team1_Predicted_Win": team1_predicted_win,
            "Probability_1": probability_1,
            "Probability_2": probability_2
        }
        return jsonify(message)

@app.route("/api/addToPredicted")
def addToPredicted():
    try:
        match_id = 1234
        if db.session.query(MatchPredictions).filter(MatchPredictions.match_id == match_id).count() == 0:
            prediction = MatchPredictions(match_id, "9.9.2020 5:00 CTE", "NaVi Jr", "VP", "link", 1, 60.0 ,40.0, 1, 2.3, 1.3)
            db.session.add(prediction)
            db.session.commit()
            return "success"
        return "match exists"
    except Exception as e:
        return e

@cron.interval_schedule(minutes=25)
def job_getstats():
    for key in list(TEAMS):       
            teamLink = TEAMS.get(key)
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN') 
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_driver_devpath = "./chromedriver"
            #chrome_prod_devpath = os.environ.get("CHROMEDRIVER_PATH")
            driver = webdriver.Chrome(ChromeDriverManager().install())
            link = 'https://www.hltv.org/team/' + teamLink 
            driver.get(link)
            #team = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[1]/div/div[1]/div[1]')
            soup = BeautifulSoup(driver.page_source, 'lxml')
            links = []
            rankDiv = soup.find('div', class_= 'ranking-info')
            Rank = rankDiv.find('span', class_= 'value').text.replace('#',"")
            for a in soup.find_all("a", class_="col-custom"):
                link = a['href']
                links.append(link)
            ADR= 0.0
            Raiting = 0.0
            KAST = 0.0
            Impact= 0.0
            DPR = 0.0
            KPR = 0.0
            baselink= 'https://www.hltv.org/stats/'
            for link in links:
                link = link.replace('player', 'players')
                endlink = baselink + link + '?startDate=2020-01-02&endDate=2020-06-03&rankingFilter=Top35'
                driver.get(endlink)
                soup = BeautifulSoup(driver.page_source, 'lxml')
                #stats are the 5 values
                stats= []
                values = soup.find_all("div", class_="summaryStatBreakdownDataValue")
                for value in values:
                    try:
                        value = float(value.text)
                    except:
                        value = value.text
                        try:
                            value = value.replace("%","")
                            value = float(value)
                        except: 
                            value = 0.0
                    #print(value)
                    stats.append(value)
                ADR = ADR + stats[4]
                Raiting = Raiting + stats[0]
                KAST = KAST + stats[2]
                Impact = Impact + stats[3]
                DPR = DPR + stats[1]
                KPR = KPR + stats[5]
            global team_stats
            team_stats[key] = [ADR, Raiting, KAST, Impact, DPR, KPR, float(Rank)]
            driver.close()
    # return str(team_stats)


@app.route('/')
def home():
    print(matches_list)
    return render_template('home.html', teams = TEAMS, matches_array = matches_list)

@app.route("/past")
def past():
    result_set = db.session.execute("SELECT * FROM match_predictions ORDER BY match_date DESC")  
    d, past_matches = {}, []
    for rowproxy in result_set:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        past_matches.append(d)
    return render_template('past.html', past_matches = past_matches, teams = TEAMS, team_stats = team_stats)

@app.route('/discarded')
def discarded():
    return str(matches_discarded)

@app.route('/api/upcoming_matches', methods=["GET"])
def upcoming_matches():
    if (request.method == 'GET'):
        global matches_list
        upcoming_matches = matches_list
        return(jsonify(upcoming_matches))
"""
@app.route('/api/upcoming_matches', methods=["GET"])
def matches_list():
    if (request.method == 'GET'):
        result_set = db.session.execute("SELECT * FROM upcoming_matches")  
        d, upcoming_matches = {}, []
        for rowproxy in result_set:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            upcoming_matches.append(d)
        return(jsonify(upcoming_matches))
"""

@app.route('/api/teamstats')
def teamstats():
    global team_stats
    return (str(team_stats))

@cron.interval_schedule(minutes = 10)
def job_getmatches():
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium import webdriver
    from bs4 import BeautifulSoup
    from selenium.webdriver.common.keys import Keys
    import time
    import math
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(ChromeDriverManager().install())
    #driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options = chrome_options)
    driver.get('https://csgolounge.com/')
    time.sleep(7)
    message = {}
    i = 0
    soup = BeautifulSoup(driver.page_source, "html5lib")
    full_matches_box = soup.find_all('div', class_='lounge-bets-items__item sys-betting bet_coming')
    for full_match_box in full_matches_box:
        i= i + 1 
        time_fixed = full_match_box.find('div', class_='lounge-match-date__date sys-time-fixed')
        time_fixed_str = time_fixed.text
        team1_str = full_match_box.find('div', class_='lounge-team__title sys-t1name').text
        team2_str = full_match_box.find('div', class_='lounge-team__title sys-t2name').text
        team1_img = full_match_box.find('img', class_='sys-t1logo')['src']
        team2_img = full_match_box.find('img', class_='sys-t2logo')['src']
        match_link = full_match_box.find('a', class_='lounge-match')['href']
        match_id = ''.join(letter for letter in match_link if letter.isdigit())
        # check if match is between two teams from the list
        contains1 = False
        contains2 = False
        for key in TEAMS:
                if team1_str.replace(" ", "")  == key.replace(" ", ""):
                    contains1 = True
                if team2_str.replace(" ", "")  == key.replace(" ", ""):
                    contains2 = True
        if (contains1 and contains2):
            # update db with prediction
            if db.session.query(MatchPredictions).filter(MatchPredictions.match_id == match_id).count() == 0:
                            response = requests.get('https://csgopredict.herokuapp.com/api/predict' + '?team1=' + team1_str.strip() + '&team2=' + team2_str.strip())
                            response = response.json()
                            prediction = MatchPredictions(match_id, time_fixed_str, team1_str, team2_str,
                                                match_link, response.get("Team1_Predicted_Win"), response.get("Probability_1"), response.get("Probability_2"), -1, 0.0 ,0.0)
                            db.session.add(prediction)
                            db.session.commit()
            if db.session.query(UpcomingMatches).filter(UpcomingMatches.match_id == match_id).count() == 0:
                            match = UpcomingMatches(match_id, time_fixed_str, team1_str, team2_str,
                                                match_link)
                            db.session.add(match)
                            print(match)
                            db.session.commit()
        else: 
            matches_discarded.append([team1_str, team2_str])
    driver.close()

@app.route('/api/creatematch')
def create_match():
    # use uuid to generate ids
    # date format: "13.09.2021, 10:00 CET"

    # generates a random id
    id = int(random.random() * 100000)

    # gets current date, year, month, day, minute, 
    now = datetime.datetime.now()

    #initializes current current year, month, day, minute, and hour; uses -z suffix declaration for clarity
    yearz = now.year
    monthz = now.month
    dayz = now.day
    hrz = now.hour
    minz = 0 if now.minute < 30 else 30

    chosenTime = 30 * random.randrange(1,8)

    minz += chosenTime

    hrz += (int)(minz/60)
    minz %= 60
    if (minz == 0):
        minz = "00"

    dayz += (int)(hrz/24)
    hrz %= 24

    monthz += (int)(dayz/31)
    dayz %= 31
    if (dayz < 10):
        dayz = "0" + str(dayz)
    

    yearz += (int)(monthz/12)
    monthz %= 12
    if (monthz < 10):
        monthz = "0" + str(monthz)

    match_date = str(dayz) + "." + str(monthz) + "." + str(yearz) + ", " + str(hrz) + ":" + str(minz) + "CET"

    teamNum = random.randrange(0, len(TEAMS))

    teamNum2 = random.randrange(0, len(TEAMS))

    if (teamNum2 == teamNum and teamNum != 0):
        teamNum -= 1
    elif (teamNum2 == teamNum):
        teamNum += 1

    team1_name = "Team1 Name"
    team2_name = "Team2 Name"
    for team1 in TEAMS:
        if (teamNum == 0):
            team1_name = team1
            break
        else:
            teamNum -= 1

    for team2 in TEAMS:
        if (teamNum2 == 0):
            team2_name = team2
            break
        else:
            teamNum2 -= 1

    match_link = "https://csgolounge/" + str(id)

    return jsonify([id, match_date, team1_name, team2_name, match_link])

def add_matches():
    x = random.randrange(3, 6)
    for count in range(x):
        new_match = create_match()
        for dict_match in matches_list:
            if ((dict_match["team1_name"] == new_match["team1_name"] and dict_match["team2_name"] == new_match["team2_name"]) or (dict_match["team2_name"] == new_match["team1_name"] and dict_match["team1_name"] == new_match["team2_name"])):
                new_match = None
                break
        if new_match == None:
            count -= 1
        else: 
            matches_list.append(new_match)
            remove_match(new_match.id)
    return
    # call create match 3-5 times
    # check if match is duplicate (exists in matches_list)
    # if not add to match_list
    # schedule remove match call at match_time + 60 mins
    # after match removed, decide who wins, add coef and add to predicted matches


def remove_match(match_id):
    match_to_remove = None
    for dict_match in matches_list:
        if dict_match["id"] == match_id:
            match_to_remove = dict_match
            break
    match_list.remove(match_to_remove)
    return
    # loop matches_list, remove match with match_id
    # this function needs to be scheduled an hour after a game starts

@cron.interval_schedule(minutes = 15)
def job_updatedb():
    result_set = db.session.execute("SELECT * FROM match_predictions ORDER BY match_date DESC")  
    d, past_matches = {}, []
    for rowproxy in result_set:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        past_matches.append(d)
    for i in range(0, len(past_matches)):
        if (past_matches[i].get('team1_won') == -1): 
            link = 'https://csgolounge.com' + past_matches[i].get('match_link')
            import time
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(link)
            time.sleep(8)
            team1_won = -1
            WINNER_COLOR = 'rgba(244, 121, 0, 1)'
            team1_div = driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div[1]/div[1]')
            team1_color = str(team1_div.value_of_css_property("color"))
            team2_div = driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]')
            team2_color = str(team2_div.value_of_css_property("color"))
            team1_coeff = driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div[1]/div[2]/div[1]').text.replace('x', "")
            team2_coeff = driver.find_element_by_xpath('/html/body/div/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[2]/div/div[1]/div[2]/div[1]').text.replace('x', "")
            if team1_color == WINNER_COLOR:
                team1_won = 1
            elif team2_color == WINNER_COLOR:
                team1_won = 0
            else:
                team1_won = -1
                team1_coeff = 0
                team2_coeff = 0
            driver.close()
            #update cells in db using that information
            match_id = past_matches[i].get('match_id')
            match = db.session.query(MatchPredictions).filter(MatchPredictions.match_id == match_id).one()
            match.team1_coeff = team1_coeff
            db.session.commit()
            match.team2_coeff = team2_coeff
            db.session.commit()
            match.team1_won = team1_won
            db.session.commit()

@cron.interval_schedule(seconds = 5, max_runs = 1)
def job_init():
    job_getstats()
    #job_getmatches()
    #job_updatedb()
    return

# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    app.run(threaded=True, use_reloader=False)




