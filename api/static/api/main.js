function router() {
  Utility.clearView();
  let url = (window.location.hash).slice(2);
  if (url == '') {
    View.homepage();
  }
  else if ((/^signup$/i).test(url)) {
    View.signupLoad();
  }
  else if ((/^signup\/submit$/i).test(url)) {
    View.signupSubmit();
  }
  else if ((/^login$/i).test(url)) {
    View.loginLoad();
  }
  else if ((/^login\/submit$/i).test(url)) {
    View.loginSubmit();
  }
  else if ((/^logout$/i).test(url)) {
    View.logout();
  }
  else if ((/^landing$/i).test(url)) {
    View.landing();
  }
  else if ((/^league\/join$/i).test(url)) {
    View.joinLeagueLoad();
  }
  else if ((/^league\/join\/submit$/i).test(url)) {
    View.joinLeagueSubmit();
  }
  else if ((/^league\/create$/i).test(url)) {
    View.createLeagueLoad();
  }
  else if ((/^league\/create\/submit$/i).test(url)) {
    View.createLeagueSubmit();
  }
  else if ((/^league\/main\/.+?$/i).test(url)) {
    let leagueName = url.slice(12);
    View.league(leagueName);
  }
  else if ((/^league\/answers\/submit$/i).test(url)) {
    View.leagueAnswersSubmit();
  }
  else if ((/^league\/answers\/.+?$/i).test(url)) {
    let leagueName = url.slice(15);
    View.leagueAnswersLoad(leagueName);
  }
  else if ((/^league\/picks\/submit$/i).test(url)) {
    View.leaguePicksSubmit();
  }
  else if ((/^league\/picks\/.+?$/i).test(url)) {
    let leagueName = url.slice(13);
    View.leaguePicksLoad(leagueName);
  }
  else if ((/^league\/scoreboard\/.+?$/i).test(url)) {
    let leagueName = url.slice(18);
    View.scoreboard(leagueName);
  }
  else {
    View.notFound();
  }
}

function addCustomRedirects() {
  let links = document.getElementsByTagName('a');
  for (let link = 0; link < links.length; link++) {
    links[link].addEventListener('click', Utility.changeHash);
  }
  let forms = document.getElementsByClassName('form-submit');
  for (let form = 0; form < forms.length; form++) {
    forms[form].addEventListener('click', Utility.changeHash);
  }
}

window.addEventListener('hashchange', router);
window.addEventListener('load', router);
window.addEventListener('load', addCustomRedirects);