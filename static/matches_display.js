
function display_matches(teams, matches_array) {
    console.log(matches_array)
    matches_array = JSON.parse(matches_array)
    //var request = new XMLHttpRequest()
    // url = 'api/upcoming_matches';
    //request.open('GET', url, true)
    // matches_array = []
    // request.onload = function () {
    //    console.log("LOADED")
    //    matches_array = JSON.parse(this.response)
    // }
    console.log(matches_array)
    teams = JSON.parse(teams)
    for (i = 0; i < matches_array.length; i++) {
        //check if team1 is one of the teams in the CONST team dictionary
        // team2_contains = checkTeam(matches_array[i][3], teams);
        // if (true) {
        console.log(matches_array.length)
        var MatchDiv = document.createElement("div");
        MatchDiv.setAttribute("class", "MatchDiv");
        var MatchHeader = document.createElement("div");
        MatchHeader.setAttribute("class", "MatchHeader");
        var MatchBody = document.createElement("div");
        MatchBody.setAttribute("class", "MatchBody");
        var timeMatch = document.createElement('p');
        timeMatch.textContent += matches_array[i].match_date;
        timeMatch.setAttribute("class", "timeMatch");
        var team1_div = document.createElement("div");
        team1_div.setAttribute("class", "team1_div");
        var team2_div = document.createElement("div");
        team2_div.setAttribute("class", "team2_div");
        var team1_name = document.createElement('p');
        team1_name.setAttribute("class", "team1_name");
        team1_name.textContent += matches_array[i].team1_name;
        var team1_img = document.createElement('img');
        team1_img.setAttribute("class", "team1_img");
        // team1_img.src = matches_array[i][4];
        team1_img.src = 'static/team_logos/' + matches_array[i].team1_name.replace(/\s/g, '') + '.png';
        var team2_name = document.createElement('p')
        team2_name.setAttribute("class", "team2_name");
        team2_name.textContent += matches_array[i].team2_name;
        var team2_img = document.createElement('img');
        team2_img.setAttribute("class", "team1_img");
        // team2_img.src = matches_array[i][5];
        team2_img.src = 'static/team_logos/' + matches_array[i].team2_name.replace(/\s/g, '') + '.png';
        var matchPrediction = document.createElement('div');
        matchPrediction.setAttribute('class', 'matchPrediction')
        matchPrediction.setAttribute('id', 'matchPrediction_' + i)
        var button = document.createElement("button");
        button.innerHTML = "Predict";
        button.setAttribute("class", "predictButton")
        button.setAttribute("data-team1", team1_name.textContent)
        button.setAttribute("data-team2", team2_name.textContent)
        button.setAttribute("data-flag", '')
        matchID = 'matchPrediction_' + i
        button.setAttribute("data-predictionID", matchID)
        button.onclick = function () {
            if (this.dataset.flag == '') {
                this.dataset.flag = 'button_clicked'
                team1_name_str = this.dataset.team1.replace(/\s/g, '')
                team2_name_str = this.dataset.team2.replace(/\s/g, '')
                MATCH_ID = this.dataset.predictionid;
                // alert(team1_name_str)
                // team2_name_str = matches_array[i][3].replace(/\s/g, '')
                var request = new XMLHttpRequest()
                url = 'api/predict' + '?team1=' + team1_name_str + '&team2=' + team2_name_str;
                // url = 'api/predict'
                request.open('GET', url, true)
                request.onload = function () {
                    var data = JSON.parse(this.response)
                    var team1_will_win = data["Team1_Predicted_Win"]
                    team1_probability = document.createElement('p')
                    team1_probability.setAttribute("class", "team1_probability")
                    team1_probability.textContent += ((Math.round(data["Probability_1"] * 1000)) / 10) + "%"
                    team2_probability = document.createElement('p')
                    team1_probability.setAttribute("id", 'prediction1_for_' + MATCH_ID)
                    team2_probability.setAttribute("id", 'prediction2_for_' + MATCH_ID)
                    team2_probability.setAttribute("class", "team2_probability")
                    team2_probability.textContent += ((Math.round(data["Probability_2"] * 1000)) / 10) + "%"
                    matchPrediction = document.getElementById(MATCH_ID)
                    matchPrediction.appendChild(team1_probability)
                    matchPrediction.appendChild(team2_probability)
                    // alert("Team to win: "  + data['Prediction_Teamname']);
                    // var predictionDiv = document.createElement("div");
                    // predictionDiv.setAttribute('class', 'predictionDiv')
                }
                request.send()
            } else {
                MATCH_ID = this.dataset.predictionid;
                matchPrediction = document.getElementById(MATCH_ID)
                team1_probability = document.getElementById('prediction1_for_' + MATCH_ID)
                team2_probability = document.getElementById('prediction2_for_' + MATCH_ID)
                matchPrediction.removeChild(team1_probability)
                matchPrediction.removeChild(team2_probability)
                this.dataset.flag = '';
            }
        };
        //display the results
        console.log("almost done")
        matchPrediction.appendChild(button)
        MatchHeader.appendChild(timeMatch);
        team1_div.appendChild(team1_name);
        team1_div.appendChild(team1_img);
        team2_div.appendChild(team2_img);
        team2_div.appendChild(team2_name);
        MatchBody.appendChild(team1_div);
        MatchBody.appendChild(team2_div);
        MatchBody.appendChild(matchPrediction);
        var MatchesDiv = document.getElementById("MatchesDiv");
        MatchDiv.appendChild(MatchHeader);
        MatchDiv.appendChild(MatchBody);
        // var team1_contains = checkTeam(matches_array[i][3], teams);
        MatchesDiv.appendChild(MatchDiv);
        console.log("all working")
        // }
    }

}


function checkTeam(teamname, teams_dict) {
    contains_team = new Boolean(false);
    for (i = 0; i < teams_dict.length; i++) {
        thisName = Object.keys(json_object[i])
        if (teamname === thisName) {
            contains_team = true;
            break;
        }
    }
    return contains_team;
}
