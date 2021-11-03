console.log("here")
function display_matches(past_matches, teams) {
    past_matches = JSON.parse(past_matches)
    teams = JSON.parse(teams)
    show_matches(past_matches);
    // show 4 more matches when button is pressed
    showDiv = document.getElementsByClassName('showDiv')[0]
    $('.showDiv').click(function() {
        $('#PastMatchesDiv div:hidden').slice(0,20).slideDown();
      });
}

function show_matches(past_matches) {
    // alert(past_matches.length)
    for (i = 0; i < past_matches.length; i++) {
        var PastMatchDiv = document.createElement("div");
        PastMatchDiv.setAttribute("class", "PastMatchDiv");
        var PastMatchBody = document.createElement("div");
        PastMatchBody.setAttribute("class", "PastMatchBody");
        var PastMatchHeader = document.createElement("div");
        PastMatchHeader.setAttribute("class", "PastMatchHeader");
        var past_timeMatch = document.createElement('p');
        past_timeMatch.textContent += past_matches[i]['match_date']; 
        past_timeMatch.setAttribute("class","past_timeMatch");
        var team1_div = document.createElement("div");
        team1_div.setAttribute("class", "past_team1_div");
        var team2_div = document.createElement("div");
        team2_div.setAttribute("class", "past_team2_div");
        var team1_name = document.createElement('p');
        var predictedDiv = document.createElement('div');
        predictedDiv.setAttribute("class", "predictedDiv");
        var predictedProbability = document.createElement('p');
        predictedProbability.setAttribute("class", "predictedProbability");
        var team2_name = document.createElement('p');
        var team1_img = document.createElement('img');
        team1_img.setAttribute("class", "past_team1_img");
        team1_img.src ='static/team_logos/' +   past_matches[i]['team1_name'].replace(/\s/g, '') + '.png';
        var team2_img = document.createElement('img');
        team2_img.setAttribute("class", "past_team2_img");
        team2_img.src ='static/team_logos/' +   past_matches[i]['team2_name'].replace(/\s/g, '') + '.png';
        team1_name.setAttribute("class", "past_team1_name");
        team2_name.setAttribute("class", "past_team2_name");
        team1_name.textContent += past_matches[i]['team1_name'];
        team2_name.textContent += past_matches[i]['team2_name'];
        var predictedTeamImg = document.createElement('img');
        var team1_coeff = document.createElement('p');
        var team2_coeff = document.createElement('p');
        team1_coeff.textContent += 'x' + past_matches[i]['team1_coeff'];
        team2_coeff.textContent += 'x' + past_matches[i]['team2_coeff'];
        team1_coeff.setAttribute("class", "past_team1_coeff");
        team2_coeff.setAttribute("class", "past_team2_coeff");
        var predictionResult = document.createElement('p');
        predictionResult.setAttribute("class", "predictionResult");
        if (past_matches[i]['team1_win'] == 0 ) {
            predictedProbability.textContent += ((Math.round(past_matches[i]['team2_probability']  * 1000))/10) + "%"
            predictedTeamImg.src = 'static/team_logos/' +   past_matches[i]['team2_name'].replace(/\s/g, '') + '.png';
        } else {
            predictedProbability.textContent +=  ((Math.round(past_matches[i]['team1_probability']  * 1000))/10) + "%"
            predictedTeamImg.src = 'static/team_logos/' +   past_matches[i]['team1_name'].replace(/\s/g, '') + '.png';
        }
        if (past_matches[i]['team1_won'] == -1) {
            predictionResult.textContent += 'In Progress';
        }
        else if (past_matches[i]['team1_win'] == past_matches[i]['team1_won']){
            predictionResult.textContent += 'Won';
            predictionResult.style.color = 'green';
        } else {
            predictionResult.textContent += 'Lost';
            predictionResult.style.color = 'red';
        }
        predictedTeamImg.setAttribute("class", "predictedTeamImg");
        if (past_matches[i]['team1_won'] != -1) {
            team1_div.appendChild(team1_coeff);
            team1_div.appendChild(team1_name);
            team1_div.appendChild(team1_img);
            team2_div.appendChild(team2_coeff);
            team2_div.appendChild(team2_img);
            team2_div.appendChild(team2_name);
            predictedDiv.appendChild(predictedProbability);
            predictedDiv.appendChild(predictedTeamImg);
            predictedDiv.appendChild(predictionResult);
            PastMatchBody.appendChild(team1_div);
            PastMatchBody.appendChild(team2_div);
            PastMatchBody.appendChild(predictedDiv);
            PastMatchHeader.appendChild(past_timeMatch);
            PastMatchDiv.appendChild(PastMatchHeader);
            PastMatchDiv.appendChild(PastMatchBody);
            var PastMatchesDiv = document.getElementById("PastMatchesDiv");
            PastMatchesDiv.appendChild(PastMatchDiv);
        }
    }
}