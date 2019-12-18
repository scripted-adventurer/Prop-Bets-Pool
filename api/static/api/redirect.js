class Redirect {
  constructor() {}

  static homepage() {
    window.location.hash = '/';
  }
  static login() {
    window.location.hash = '/login';
  }
  static signup() {
    window.location.hash = '/signup';
  }
  static landing() {
    window.location.hash = '/landing';
  }
  static leagueHome(leagueName) {
    window.location.hash = '/league/main/' + leagueName;
  }
}