# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client

from ui.forms import SignUpForm
from classes.tests import DataSetup
import classes.user
import ui.models as db_models

class ViewsTest(TestCase):
  
  def auth_test(self, url):
    print('%s: authorization test' % url)
    client = Client()
    # check that unauthenticated requests are redirected to the login page
    response = client.get(url)
    self.assertEqual(response.url, '/accounts/login/?next=%s' % url)
    self.assertEqual(response.status_code, 302)

  def custom_test(self, url, method, response_template, response_context, 
    payload={}, status_code=200, username='', password='password'):
    print('%s: custom test' % url)
    client = Client()
    if username:
      client.login(username=username, password=password)
    if method == 'GET':
      response = client.get(url)
    elif method == 'POST':
      response = client.post(url, payload)
    else:
      return 0
    self.assertEqual(response.status_code, status_code)
    self.assertEqual(response.templates[0].name, response_template)
    if response_context:
      for key, value in response_context.items():
        self.assertEqual(response.context[key], value)

  def test_homepage(self):
    url = '/'
    response_template = 'ui/home.html'
    response_context = {}
    self.custom_test(url, 'GET', response_template, response_context)

  def test_signup(self):
    url = '/ui/signup'
    response_template = 'ui/signup.html'
    response_context = {}
    self.custom_test(url, 'GET', response_template, response_context) 

  def test_login(self):
    url = '/accounts/login/'
    response_template = 'registration/login.html'
    response_context = {}
    self.custom_test(url, 'GET', response_template, response_context)

  def test_landing(self):
    data = DataSetup('ui_landing')
    data.create_users(2)
    data.create_leagues(2)
    data.create_member(data.user[0].get_object(), data.league[0], True)
    data.create_member(data.user[0].get_object(), data.league[1], False)
    url = '/ui/main'
    response_template = 'ui/landing.html'
    username = data.user[1].name

    self.auth_test(url)

    # no leagues
    response_context = {'user': data.user[1].get_object(), 'leagues': [], 
      'message': ''}
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # multiple leagues
    username = data.user[0].name
    response_context = {'user': data.user[0].get_object(), 'leagues': [
      data.league[0].name, data.league[1].name], 'message': ''}
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)

  def test_join_league(self):
    data = DataSetup('ui_join_league')
    data.create_users(1)
    url = '/ui/league/join'
    response_template = 'ui/league_join.html'
    username = data.user[0].name
    response_context = {'message': ''}

    self.auth_test(url)
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)

  def test_join_league_submit(self):
    data = DataSetup('ui_join_league_submit')
    data.create_users(1)
    data.create_leagues(1)  
    url = '/ui/league/join/submit'
    username = data.user[0].name

    self.auth_test(url)

    response_context = {'message': 
      'Error: League name and/or password is invalid or missing.'}
    response_template = 'ui/landing.html'
    # invalid league
    payload = {'leagueName': 'invalid_league', 'leaguePassword': 'password'}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # missing league
    payload = {'leaguePassword': 'password'}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # invalid password
    payload = {'leagueName': data.league[0].name, 'leaguePassword': 
      'invalid_password'}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # missing password
    payload = {'leagueName': data.league[0].name}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # valid
    payload = {'leagueName': data.league[0].name, 'leaguePassword': 'password'}
    response_context = {'message': 'Successfully joined league.'}
    response_template = 'ui/league_home.html'
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # check data is created
    member = db_models.Member.objects.get(user=data.user[0].get_object(), 
      league=data.league[0], admin=False)

  def test_create_league(self):
    data = DataSetup('ui_create_league')
    data.create_users(1)
    url = '/ui/league/create'
    response_template = 'ui/league_create.html'
    username = data.user[0].name
    response_context = {'message': ''}

    self.auth_test(url)
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)

  def test_create_league_submit(self):
    data = DataSetup('ui_create_league_submit')
    data.create_users(1)
    data.create_leagues(1)  
    url = '/ui/league/create/submit'
    username = data.user[0].name

    self.auth_test(url)

    response_template = 'ui/league_create.html'
    response_context = {'message': 
      'Error: League name, password, and/or prop bet list is invalid or missing.'}
    # missing league name
    payload = {'leaguePassword': 'password', 'propBetList': 
      'Test Prop Bet 1\nTest Prop Bet 2\nTest Prop Bet 3'}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # missing password
    payload = {'leagueName': 'unique_league_name', 'propBetList': 
      'Test Prop Bet 1\nTest Prop Bet 2\nTest Prop Bet 3'}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # missing prop bet list
    payload = {'leagueName': 'unique_league_name', 'leaguePassword': 'password'}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # not unique
    response_context = {'message': 'Error: League name must be unique.'}
    payload = {'leagueName': data.league[0].name, 'leaguePassword': 'password', 
      'propBetList': 'Test Prop Bet 1\nTest Prop Bet 2\nTest Prop Bet 3'}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # valid
    response_template = 'ui/league_home.html'
    response_context = {'message': 'Successfully created league.'}
    payload = {'leagueName': 'unique_league_name', 'leaguePassword': 'password', 
      'propBetList': 'Test Prop Bet 1\nTest Prop Bet 2\nTest Prop Bet 3'}
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # check data is created
    new_league = db_models.League.objects.get(name='unique_league_name')
    new_member = db_models.Member.objects.get(user=data.user[0].get_object(), 
      league=new_league, admin=True)
    new_prop_bets = db_models.PropBet.objects.filter(league=new_league)
    new_prop_bets = [row.title for row in new_prop_bets]
    self.assertEqual(new_prop_bets, ['Test Prop Bet 1', 'Test Prop Bet 2', 
      'Test Prop Bet 3'])

  def test_league(self):
    data = DataSetup('ui_league')
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], True)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    url = '/ui/league/home/%s' % data.league[0].name

    self.auth_test(url)

    response_template = 'ui/landing.html'
    response_context = {'message': 'Error: League is invalid or you are not a member.'}
    # invalid league
    url = '/ui/league/home/invalid_league'
    username = data.user[0].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # not member
    url = '/ui/league/home/%s' % data.league[0].name
    username = data.user[2].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # member, admin
    response_template = 'ui/league_home.html'
    response_context = {'message': '', 'admin': True, 'user': 
      data.user[0].get_object(), 'league': data.league[0]}
    username = data.user[0].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # member, not admin
    response_template = 'ui/league_home.html'
    response_context = {'message': '', 'admin': False, 'user': 
      data.user[1].get_object(), 'league': data.league[0]}
    username = data.user[1].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)

  def test_league_answers(self):
    data = DataSetup('ui_league_answers')
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], True)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    url = '/ui/league/answers/%s' % data.league[0].name

    self.auth_test(url)

    response_template = 'ui/landing.html'
    response_context = {'message': 
      'Error: League is invalid or you are not a member.'}
    # not member
    username = data.user[2].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # invalid league
    url = '/ui/league/answers/invalid_league'
    username = data.user[0].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    url = '/ui/league/answers/%s' % data.league[0].name
    # not admin
    username = data.user[1].name 
    response_template = 'ui/league_home.html'
    response_context = {'message': 
      'Error: You must be an admin to update league answers.'}
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # valid
    username = data.user[0].name 
    response_template = 'ui/league_entry.html'
    response_context = {'user': data.user[0].get_object(), 'league_name': 
      data.league[0].name, 'answers': True, 'prop_bets': {data.prop_bet[0].title: 
      True, data.prop_bet[1].title: True, data.prop_bet[2].title: True}}
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)

  def test_league_answers_submit(self):
    data = DataSetup('ui_league_answers_submit')
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], True)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    url = '/ui/league/answers/submit'

    self.auth_test(url)

    response_template = 'ui/landing.html'
    response_context = {'message': 
      'Error: League is invalid or you are not a member.'}
    payload = {'league_name': data.league[0].name, data.prop_bet[0].title: False, 
      data.prop_bet[1].title: False, data.prop_bet[2].title: False}
    # not member
    username = data.user[2].name
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # invalid league
    payload = {'league_name': 'invalid_league', data.prop_bet[0].title: False, 
      data.prop_bet[1].title: False, data.prop_bet[2].title: False}
    username = data.user[0].name
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    response_template = 'ui/league_home.html'
    # missing answers
    response_context = {'message': 'Error: Answers block is invalid or missing.'}
    payload = {'league_name': data.league[0].name}
    username = data.user[0].name
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # not admin
    response_context = {'message': 'Error: You must be an admin to update league answers.'}
    payload = {'league_name': data.league[0].name, data.prop_bet[0].title: False, 
      data.prop_bet[1].title: False, data.prop_bet[2].title: False}
    username = data.user[1].name
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # valid
    response_context = {'message': 'Successfully updated league answers.'}
    username = data.user[0].name
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # check data is updated
    for x in range(0, 3):
      db_models.PropBet.objects.get(title=data.prop_bet[x].title, 
        league=data.league[0], answer=False)

  def test_league_picks(self):
    data = DataSetup('ui_league_picks')
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], True)
    data.create_member(data.user[1].get_object(), data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_pick(data.member[0], data.prop_bet[0], False)
    data.create_pick(data.member[0], data.prop_bet[1], False)
    data.create_pick(data.member[0], data.prop_bet[2], False)
    url = '/ui/league/picks/%s' % data.league[0].name

    self.auth_test(url)

    response_template = 'ui/landing.html'
    response_context = {'message': 
      'Error: League is invalid or you are not a member.'}
    # not member
    username = data.user[2].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # invalid league
    username = data.user[0].name
    url = '/ui/league/picks/invalid_league'
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    url = '/ui/league/picks/%s' % data.league[0].name
    # valid without picks
    username = data.user[1].name
    response_template = 'ui/league_entry.html'
    response_context = {'user': data.user[1].get_object(), 'league_name': 
      data.league[0].name, 'answers': False, 'prop_bets': 
      {data.prop_bet[0].title: None, data.prop_bet[1].title: None, 
      data.prop_bet[2].title: None}}
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # valid with picks
    username = data.user[0].name
    response_context = {'user': data.user[0].get_object(), 'league_name': 
      data.league[0].name, 'answers': False, 'prop_bets': 
      {data.prop_bet[0].title: False, data.prop_bet[1].title: False, 
      data.prop_bet[2].title: False}} 
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)

  def test_league_picks_submit(self):
    data = DataSetup('ui_league_picks_submit')
    data.create_users(2)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    url = '/ui/league/picks/submit'

    self.auth_test(url)

    response_template = 'ui/landing.html'
    response_context = {'message': 
      'Error: League is invalid or you are not a member.'}
    payload = {'league_name': data.league[0].name, data.prop_bet[0].title: False, 
      data.prop_bet[1].title: False, data.prop_bet[2].title: False}
    # not member
    username = data.user[1].name 
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # invalid league
    payload = {'league_name': 'invalid_league', data.prop_bet[0].title: False, 
      data.prop_bet[1].title: False, data.prop_bet[2].title: False}
    username = data.user[0].name
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    response_template = 'ui/league_home.html'
    # missing picks
    response_context = {'message': 'Error: Picks block is invalid or missing.'}
    payload = {'league_name': data.league[0].name}
    username = data.user[0].name 
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # valid
    response_context = {'message': 'Successfully updated picks.'}
    payload = {'league_name': data.league[0].name, data.prop_bet[0].title: False, 
      data.prop_bet[1].title: False, data.prop_bet[2].title: False}
    username = data.user[0].name 
    self.custom_test(url, 'POST', response_template, response_context, 
      payload=payload, username=username)
    # check data is updated
    for x in range(0, 3):
      db_models.Pick.objects.get(member=data.member[0], prop_bet=data.prop_bet[x], 
        response=False)

  def test_scoreboard(self):
    data = DataSetup('ui_scoreboard')
    data.create_users(4)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_member(data.user[2].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_pick(data.member[0], data.prop_bet[0], True)
    data.create_pick(data.member[0], data.prop_bet[1], False)
    data.create_pick(data.member[0], data.prop_bet[2], True)
    data.create_pick(data.member[1], data.prop_bet[0], False)
    data.create_pick(data.member[1], data.prop_bet[1], False)
    data.create_pick(data.member[1], data.prop_bet[2], False)
    data.create_pick(data.member[2], data.prop_bet[0], False)
    data.create_pick(data.member[2], data.prop_bet[1], True)
    data.create_pick(data.member[2], data.prop_bet[2], False)
    url = '/ui/league/scoreboard/%s' % data.league[0].name

    self.auth_test(url)

    response_template = 'ui/landing.html'
    response_context = {'message': 
      'Error: League is invalid or you are not a member.'}
    # invalid league
    username = data.user[0].name 
    url = '/ui/league/scoreboard/invalid_league'
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # not member
    username = data.user[3].name 
    url = '/ui/league/scoreboard/%s' % data.league[0].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)
    # valid
    response_template = 'ui/league_scoreboard.html'
    response_context = {'scores': [{'username': data.user[0].name, 'score': 3}, 
      {'username': data.user[1].name, 'score': 1}, 
      {'username': data.user[2].name, 'score': 0}]}
    username = data.user[1].name
    self.custom_test(url, 'GET', response_template, response_context, 
      username=username)     