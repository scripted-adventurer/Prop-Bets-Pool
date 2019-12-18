class View {
  constructor() {}

  static homepage() {
    Utility.load('main-page', '', false);
  }
  static signupLoad() {
    Utility.load('signup', '', false);
  }
  static async signupSubmit() {
    let formData = Utility.formData('signup-form');
    let requestBody = {'username': formData.get('username'), 'email': 
      formData.get('email'), 'password1': formData.get('password1'), 'password2': 
      formData.get('password2')};
    let url = '/api/signup';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      Redirect.login();
    }
    else {
      Redirect.signup();
    }
  }
  static loginLoad() {
    Utility.load('login', '', false);
  }
  static async loginSubmit() {
    let formData = Utility.formData('login-form');
    let requestBody = {'username': formData.get('username'), 'password': 
      formData.get('password')};
    let url = '/api/login';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      Utility.showLoggedInHeader();
      // update csrf token (must be refreshed after login)
      let csrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
      csrf.value = response.csrf_token;
      Redirect.landing();
    }
    else {
      Redirect.login();
    }
  }
  static async logout() {
    let requestBody = {};
    let url = '/api/logout';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      Utility.showLoggedOutHeader();
    }
    Redirect.homepage();
  }
  static async landing() {
    Utility.load('landing', 'leagues-list', true);
    let requestBody = {};
    let url = '/api/user/leagues';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      let list = document.getElementById('leagues-list');
      for (let i = 0; i < response.leagues.length; i++) {
        let league = response.leagues[i];
        let p = document.createElement('p');
        let a = document.createElement('a');
        a.innerHTML = league;
        a.href = '/#/league/main/' + league;
        a.addEventListener('click', Utility.changeHash);
        list.appendChild(p);
        p.appendChild(a);
      }
    }
  }
  static joinLeagueLoad() {
    Utility.load('league-join', '', true);
  }
  static async joinLeagueSubmit() {
    let formData = Utility.formData('league-join-form');
    let requestBody = {'league_name': formData.get('leagueName'), 'password': 
      formData.get('leaguePassword')};
    let url = '/api/league/join';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      Redirect.leagueHome(formData.get('leagueName'));
    }
    else {
      Redirect.landing();
    }
  }
  static createLeagueLoad() {
    Utility.load('league-create', '', true);
  }
  static async createLeagueSubmit() {
    let formData = Utility.formData('league-create-form');
    let requestBody = {'league_name': formData.get('leagueName'), 'password': 
      formData.get('leaguePassword'), 'prop_bets': formData.get('propBets')};
    let url = '/api/league/create';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      Redirect.leagueHome(formData.get('leagueName'));
    }
    else {
      Redirect.landing();
    }
  }  
  static async league(leagueName) {
    Utility.load('league-home', 'answers-button-container', true);
    // add league name to the header
    let header = document.getElementById('league-name');
    header.innerHTML = leagueName;
    // add the league name to the picks and scoreboard links
    let picks = document.getElementById('picks-button');
    picks.href = '/#/league/picks/' + leagueName;
    let scoreboard = document.getElementById('scoreboard-button');
    scoreboard.href = '/#/league/scoreboard/' + leagueName;
    let requestBody = {'league_name': leagueName};
    let url = '/api/member/admin';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      if (response.admin) {
        let container = document.getElementById('answers-button-container');
        let button = document.createElement('button');
        button.type = 'button';
        let a = document.createElement('a');
        a.href = '/#/league/answers/' + leagueName;
        a.innerHTML = 'Update Answers';
        a.addEventListener('click', Utility.changeHash);
        container.appendChild(button);
        button.appendChild(a);
      }
    }
    else {
      Redirect.landing();
    }
  }
  static loadPropBetsForm(dataToAdd, containerId) {
    var container = document.getElementById(containerId);
    for (let title of Object.keys(dataToAdd)) {
      let p = document.createElement('p');
      p.innerHTML = title;
      let labelTrue = document.createElement('label');
      labelTrue.innerHTML = 'True';
      labelTrue.htmlFor = title + '-true';
      let labelFalse = document.createElement('label');
      labelFalse.innerHTML = 'False';
      labelFalse.htmlFor = title + '-false';
      let inputTrue = document.createElement('input');
      inputTrue.id = title + '-true';
      inputTrue.type = 'radio';
      inputTrue.name = title;
      inputTrue.value = 'true';
      let inputFalse = document.createElement('input');
      inputFalse.id = title + '-false';
      inputFalse.type = 'radio';
      inputFalse.name = title;
      inputFalse.value = 'false';
      if (dataToAdd[title] == true) {
        inputTrue.checked = 'checked';
      }
      else if (dataToAdd[title] == false) {
        inputFalse.checked = 'checked';
      }
      container.appendChild(p);
      p.appendChild(inputTrue);
      p.appendChild(labelTrue);
      p.appendChild(inputFalse);
      p.appendChild(labelFalse);
    }
  }
  static async leagueAnswersLoad(leagueName) {
    Utility.load('league-answers', 'answers-container', true);
    let requestBody = {'league_name': leagueName};
    let url = '/api/league/prop-bets';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      // set the hidden league name field
      let leagueNameField = document.getElementById('league-answers-name');
      leagueNameField.value = leagueName;
      let dataToAdd = response.prop_bets;
      this.loadPropBetsForm(dataToAdd, 'answers-container');
    }
    else {
      Redirect.landing();
    }
  }
  static async leagueAnswersSubmit() {
    let leagueName = document.getElementById('league-answers-name').value;
    let formData = Utility.formData('league-answers-form');
    let answers = {}
    for (let pair of formData.entries()) {
      if (pair[1] == 'true') {
        answers[pair[0]] = true;
      }
      else {
        answers[pair[0]] = false;
      }
    }
    let requestBody = {'league_name': leagueName, 'answers': answers};
    let url = '/api/league/answers';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      Redirect.leagueHome(leagueName);
      Utility.displayMessage('Successfully updated league answers.');
    }
    else {
      Redirect.landing();
    }
  }
  static async leaguePicksLoad(leagueName) {
    Utility.load('league-picks', 'picks-container', true);
    let requestBody = {'league_name': leagueName};
    let url = '/api/member/picks/get';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      // set the hidden league name field
      let leagueNameField = document.getElementById('league-picks-name');
      leagueNameField.value = leagueName;
      let dataToAdd = response.picks;
      this.loadPropBetsForm(dataToAdd, 'picks-container');
    }
    else {
      Redirect.landing();
    }
  }
  static async leaguePicksSubmit() {
    let leagueName = document.getElementById('league-picks-name').value;
    let formData = Utility.formData('league-picks-form');
    let picks = {}
    for (let pair of formData.entries()) {
      if (pair[1] == 'true') {
        picks[pair[0]] = true;
      }
      else {
        picks[pair[0]] = false;
      }
    }
    let requestBody = {'league_name': leagueName, 'picks': picks};
    let url = '/api/member/picks/update';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      Redirect.leagueHome(leagueName);
      Utility.displayMessage('Successfully updated picks.');
    }
    else {
      Redirect.landing();
    }
  }  
  static async scoreboard(leagueName) {
    Utility.load('league-scoreboard', 'scoreboard-table', true);
    let requestBody = {'league_name': leagueName};
    let url = '/api/league/scoreboard';
    let response = await Utility.submit(url, requestBody);
    if (response) {
      let scores = response.scoreboard;
      let table = document.getElementById('scoreboard-table');
      for (let i = 0; i < scores.length; i++) {
        let score = scores[i];
        let username = score.username;
        let total = score.score;
        let tr = document.createElement('tr');
        let td1 = document.createElement('td');
        td1.innerHTML = username;
        let td2 = document.createElement('td');
        td2.innerHTML = total;
        table.appendChild(tr);
        tr.appendChild(td1);
        tr.appendChild(td2);
      }
    }
    else {
      Redirect.landing();
    }
  }
  static notFound() {
    let template = document.getElementById('not-found');
    template.style.display = 'block';
  }  
}