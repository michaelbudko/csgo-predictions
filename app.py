from flask import Flask, Response, render_template, url_for, request, jsonify
import time, math, random
import json
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
    hashcode = db.Column(db.BigInteger, primary_key = True)
    match_date = db.Column(db.String(100))
    team1_name = db.Column(db.String(100))
    team2_name = db.Column(db.String(100))
    match_link = db.Column(db.String(100))
    team1_win  =  db.Column(db.Integer)
    team1_probability  =  db.Column(db.Float)
    team2_probability =  db.Column(db.Float)

    def __init__(self, hashcode, match_date, team1_name, team2_name, 
                match_link, team1_win, team1_probability, team2_probability):
                self.hashcode = hashcode
                self.match_date = match_date
                self.team1_name = team1_name
                self.team2_name = team2_name
                self.match_link = match_link
                self.team1_win = team1_win
                self.team1_probability = team1_probability
                self.team2_probability = team2_probability

matches_list = []
matches_discarded = []
team_stats ={}
TEAMS = {
#   "Na'Vi": "4608/natus-vincere",
#   "Fnatic": "4991/fnatic",
#   "Astralis": "6665/astralis",
#   "mousesports" : "4494/mousesports", 
  "G2" : "5995/g2",
#   "Liquid" : "5973/liquid",
#   "EG" : "10399/evil-geniuses",
#   "FaZe" : "6667/faze",
#   "100 Thieves" : "8474/100-thieves",
#   "NiP" : "4411/nip",
#   "OG" : "10503/og",
#   "BIG" : "7532/big",
#   "mibr" : "9215/mibr",
#    "Ence" : "4869/ence",
  "Godsent" : "6902/godsent",
    # "Renegades" : "6211/renegades",
    # "Cloud9" : "5752/cloud9",
    # "Sprout" : "8637/sprout",
    # "Vitality" : "9565/vitality",
    # "pro100" : "7898/pro100",
    # "Heretics" : "8346/heretics",
    # "coL" : "5005/complexity",
    # "forZe" : "8135/forze",
    # "FURIA" : "8297/furia",
    # "Spirit" : "7020/spirit",
#   "North" : "7533/north",
#   "HAVU" : 7865/havu",
    # "VP" : "5378/virtuspro",
    # "MAD Lions" : "8362/mad-lions"
#   "Gen.G" : "10514/geng",
#   'Winstrike': '9183/winstrike',
#   'c0ntact': '10606/c0ntact',
#   'Heroic': '7175/heroic',
#   'Secret': '10488/secret',
#   "Espada": '8669/espada',
#   'Hard Legion': "10421/hard-legion",
}


with open(f'CSGOmodel.pkl', 'rb') as f:
    model = pickle.load(f)

cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()

@app.route("/api/matches", methods=["GET", "POST"])
def api_matches():
    if(request.method == 'POST'): 
        global matches_list 
        matches_list = []
        matches_json = request.get_json()
        for match_json in matches_json:
            contains1 = False
            contains2 = False
            for key in TEAMS:
                if matches_json.get(match_json)[2].replace(" ", "")  == key:
                    contains1 = True
                if matches_json.get(match_json)[3].replace(" ", "")  == key:
                    contains2 = True
            if (contains1 and contains2):
                # add to list of matches (global var)
                matches_list.append(matches_json.get(match_json))
                # predict result and store in the database
                # time_fixed_str, team1_str, team2_str, team1_img, team2_img, match_link
                # time_fixed_str = matches_json.get(match_json)[1]
                # team1_str = matches_json.get(match_json)[2]
                # team2_str = matches_json.get(match_json)[3]
                # match_link = matches_json.get(match_json)[6].strip()
                # hashcode_str = time_fixed_str.strip() + team1_str.strip() + team2_str.strip()
                # hashcode = int(abs(hash(hashcode_str)) % (13 ** 5))
                # #check if match has been predicted in the database
                # if db.session.query(MatchPredictions).filter(MatchPredictions.hashcode == hashcode).count() == 0:
                #         response = requests.get('https://csgopredict.herokuapp.com/api/predict' + '?team1=' + team1_str.strip() + '&team2=' + team2_str.strip())
                #         response = response.json()
                #         prediction = MatchPredictions(str(hashcode), time_fixed_str, team1_str, team2_str,
                #                             match_link, response.get("Team1_Predicted_Win"), response.get("Probability_1"), response.get("Probability_2"))
                #         db.session.add(prediction)
                #         db.session.commit()
                #         #handle exception (model not loaded)
            else:
                matches_discarded.append(matches_json.get(match_json)[2] + ' ' + matches_json.get(match_json)[3])
        return jsonify(matches_json)

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


@cron.interval_schedule(minutes=25)
def job_getstats():
    for key in list(TEAMS):       
            teamLink = TEAMS.get(key)
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options = chrome_options)
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
            team_stats[key] = [ADR, Raiting, KAST, Impact, DPR, KPR, float(Rank)]
            driver.close()
    # return str(team_stats)


@app.route('/')
def home():
    return render_template('home.html', matches = matches_list, teams = TEAMS, team_stats = team_stats)

@app.route('/discarded')
def discarded():
    return str(matches_discarded)

@cron.interval_schedule(minutes = 10)
def job_getmatches():
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium import webdriver
    from bs4 import BeautifulSoup
    from selenium.webdriver.common.keys import Keys
    import time
    import math
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options = chrome_options)
    driver.get('https://csgolounge.com/')
    time.sleep(7)
    message = {}
    i = 0
    soup = BeautifulSoup(driver.page_source, "html5lib")
    full_matches_box = soup.find_all('div', class_='lounge-bets-items__item sys-betting bet_coming')
    matches = []
    for full_match_box in full_matches_box:
        i= i +1 
        time_fixed = full_match_box.find('div', class_='lounge-match-date__date sys-time-fixed')
        time_fixed_str = time_fixed.text
        team1_str = full_match_box.find('div', class_='lounge-team__title sys-t1name').text
        team2_str = full_match_box.find('div', class_='lounge-team__title sys-t2name').text
        team1_img = full_match_box.find('img', class_='sys-t1logo')['src']
        team2_img = full_match_box.find('img', class_='sys-t2logo')['src']
        match_link = full_match_box.find('a', class_='lounge-match')['href']
        contains1 = False
        contains2 = False
        for key in TEAMS:
            if team1_str.replace(" ", "")  == key:
                contains1 = True
            if team2_str.replace(" ", "")  == key:
                contains2 = True
        if (contains1 and contains2):
            matches_list.append([str(tens)+ str(ones), time_fixed_str, team1_str, team2_str, team1_img, team2_img, match_link])
    #     matches.append([time_fixed_str, team1_str, team2_str])
        tens = math.floor(i/10) 
        ones = i % 10
        message['match'+ str(tens)+ str(ones)] = [str(tens)+ str(ones), time_fixed_str, team1_str, team2_str, team1_img, team2_img, match_link]  
    driver.close()
    import requests
    r = requests.post('https://csgopredict.herokuapp.com/api/matches', json=message)
    r.status_code
    r.json()

@cron.interval_schedule(seconds = 5, max_runs = 1)
def job_init():
    job_getstats()
    print team_stats
    job_getmatches()

# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    app.run(threaded=True, use_reloader=False)
    # job_function()








    # https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c