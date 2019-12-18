# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
import json

from django.test import TestCase
from django.test import Client

from classes.tests import DataSetup
import classes.user
import ui.models as db_models

class ViewTest(TestCase):

  def auth_test(self, url, request):
    print('%s: authorization test' % url)
    client = Client()
    # check that unauthenticated requests are redirected to the login page
    response = client.post(url, request, 'application/json')
    self.assertEqual(response.status_code, 401)
    self.assertEqual(json.loads(response.content), {'success': False, 
      'errors': ['Authentication required.']})

  def parameter_checks(self, url, request, username='', password='password'):
    print('%s: parameter tests' % url)
    client = Client()
    if username:
      client.login(username=username, password=password)
    for param in request.keys():
      this_request = copy.deepcopy(request)
      for param_type in ['null', 'missing']:
        if param_type == 'null':
          this_request[param] = ''
        else:
          this_request.pop(param)
        this_response = client.post(url, this_request, 'application/json')
        self.assertEqual(this_response.status_code, 400)
        self.assertEqual(json.loads(this_response.content), {'success': False, 
          'errors': ['Missing or invalid data for %s' % param]})

  def custom_test(self, url, request, response, username='', status_code=200,  
    password='password'):
    print('API - %s: custom test' % url)
    client = Client()
    if username:
      client.login(username=username, password=password)
    response_object = client.post(url, request, 'application/json')
    self.assertEqual(response_object.status_code, status_code)
    self.assertEqual(json.loads(response_object.content), response)  

  def test_signup(self):
    data = DataSetup('api_signup')
    data.create_users(1)

    url = '/api/signup'
    request = {'username': 'new_username_test_signup', 'password1': 'password', 
      'password2': 'password'}
    self.parameter_checks(url, request)

    # username taken
    request = {'username': data.user[0].name, 'email': '', 
      'password1': 'password', 'password2': 'password'}
    response = {'success': False, 'errors': ['Username is already taken.']}
    self.custom_test(url, request, response)
    # passwords don't match
    request = {'username': 'api_signup_user_2', 'email': '', 
      'password1': 'newpassword', 'password2': 'password'}
    response = {'success': False, 'errors': ['Passwords do not match.']}
    self.custom_test(url, request, response)
    # valid with email
    request = {'username': 'api_signup_user_2', 'email': '', 
      'password1': 'password', 'password2': 'password'}
    response = {'success': True}
    self.custom_test(url, request, response)
    # valid without email
    request = {'username': 'api_signup_user_3', 'email': 'test@fake.com', 
      'password1': 'password', 'password2': 'password'}
    self.custom_test(url, request, response)

    # check data is created
    user1 = classes.user.User(name='api_signup_user_2').get_object()
    self.assertNotEqual(user1, None)
    user2 = classes.user.User(name='api_signup_user_3').get_object()
    self.assertNotEqual(user2, None)

  def test_login(self):
    data = DataSetup('api_login')
    data.create_users(1)

    url = '/api/login'
    request = {'username': data.user[0].name, 'password': 'password'}
    self.parameter_checks(url, request)

    # invalid username
    request = {'username': 'invalid_username', 'password': 'password'}
    response = {'success': False, 'errors': 
      ['Username and/or password is incorrect.']}
    self.custom_test(url, request, response)
    # invalid password
    request = {'username': data.user[0].name, 'password': 'invalid_password'}
    self.custom_test(url, request, response)
    # valid, csrf token returned is dynamic, so skip validating it
    request = {'username': data.user[0].name, 'password': 'password'}
    response = {'success': True}
    print('API - %s: custom test' % url)
    client = Client()
    response_object = client.post(url, request, 'application/json')
    self.assertEqual(response_object.status_code, 200)
    self.assertEqual(json.loads(response_object.content)['success'], True) 

  def test_logout(self):
    data = DataSetup('api_logout')
    data.create_users(1)

    url = '/api/logout'
    request = {}
    response = {'success': True}

    # unauthenticated
    self.custom_test(url, request, response)
    # authenticated 
    username = data.user[0].name
    self.custom_test(url, request, response, username)

  def test_user_leagues(self):
    data = DataSetup('api_user_leagues')
    data.create_users(2)
    data.create_leagues(1)
    data.create_member(data.user[0].db_object, data.league[0], False)

    url = '/api/user/leagues'
    request = {}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)
    
    # no leagues
    response = {'success': True, 'leagues': []}
    username = data.user[1].name
    self.custom_test(url, request, response, username)
    # valid
    response = {'success': True, 'leagues': [data.league[0].name]}
    username = data.user[0].name
    self.custom_test(url, request, response, username)

  def test_league_create(self):
    data = DataSetup('api_league_create')
    data.create_users(1)
    data.create_leagues(1)
    
    url = '/api/league/create'
    request = {'league_name': 'api_league_create_league_2', 'password': 'password', 
      'prop_bets': 'Test Prop Bet 1\nTest Prop Bet 2\nTest Prop Bet 3'}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)

    # duplicate name
    request = {'league_name': data.league[0].name, 'password': 'password', 
      'prop_bets': 'Test Prop Bet 1\nTest Prop Bet 2\nTest Prop Bet 3'}
    response = {'success': False, 'errors': ['League name is taken.']}
    self.custom_test(url, request, response, username)
    # valid
    request = {'league_name': 'api_league_create_league_2', 'password': 'password', 
      'prop_bets': 'Test Prop Bet 1\nTest Prop Bet 2\nTest Prop Bet 3'}
    response = {'success': True}
    self.custom_test(url, request, response, username)
    # check data is created
    new_league = db_models.League.objects.get(name='api_league_create_league_2')
    new_member = db_models.Member.objects.get(user=data.user[0].get_object(), 
      league=new_league, admin=True)
    new_prop_bets = db_models.PropBet.objects.filter(league=new_league)
    new_prop_bets = [row.title for row in new_prop_bets]
    self.assertEqual(new_prop_bets, ['Test Prop Bet 1', 'Test Prop Bet 2', 
      'Test Prop Bet 3'])

  def test_league_join(self):
    data = DataSetup('api_league_join') 
    data.create_users(1)
    data.create_leagues(1)

    url = '/api/league/join'
    request = {'league_name': data.league[0].name, 'password': 'password'}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)

    # invalid league
    request = {'league_name': 'invalid_league', 'password': 'password'}
    response = {'success': False, 'errors': ['League name and password do not match.']}
    self.custom_test(url, request, response, username)
    # invalid password
    request = {'league_name': data.league[0].name, 'password': 'invalid_password'}
    self.custom_test(url, request, response, username)
    # valid 
    request = {'league_name': data.league[0].name, 'password': 'password'}
    response = {'success': True}
    self.custom_test(url, request, response, username)
    # check data is created
    member = db_models.Member.objects.get(user=data.user[0].get_object(), 
      league=data.league[0], admin=False)  

  def test_league_prop_bets(self):
    data = DataSetup('api_league_prop_bets')
    data.create_users(2)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], False)
    data.create_prop_bet(data.league[0], False)

    url = '/api/league/prop-bets'
    request = {'league_name': data.league[0].name}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)

    # invalid league
    request = {'league_name': 'invalid_league'}
    response = {'success': False, 'errors': ['League and user do not match.']}
    self.custom_test(url, request, response, username)
    # not in league
    request = {'league_name': data.league[0].name}
    username = data.user[1].name
    self.custom_test(url, request, response, username)
    # valid 
    request = {'league_name': data.league[0].name}
    response = {'success': True, 'prop_bets': {data.prop_bet[0].title: False, 
      data.prop_bet[1].title: False}}
    username = data.user[0].name  
    self.custom_test(url, request, response, username)

  def test_league_answers(self):
    data = DataSetup('api_league_answers')
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], True)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], False)
    data.create_prop_bet(data.league[0], False)
    data.create_prop_bet(data.league[0], False)

    url = '/api/league/answers'
    request = {'league_name': data.league[0].name, 
      'answers': {data.prop_bet[0].title: True, data.prop_bet[1].title: True, 
      data.prop_bet[2].title: True}}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)

    # invalid league
    request = {'league_name': 'invalid_league', 'answers': 
      {data.prop_bet[0].title: True, data.prop_bet[1].title: True, 
      data.prop_bet[2].title: True}}
    response = {'success': False, 'errors': 
      ['League and user do not match (user must be admin).']}
    self.custom_test(url, request, response, username)
    # not in league
    request = {'league_name': data.league[0].name, 
      'answers': {data.prop_bet[0].title: True, data.prop_bet[1].title: True, 
      data.prop_bet[2].title: True}}
    username = data.user[2].name
    self.custom_test(url, request, response, username)
    # not admin
    username = data.user[1].name
    self.custom_test(url, request, response, username)
    # valid
    response = {'success': True}
    username = data.user[0].name
    self.custom_test(url, request, response, username)
    # check data is created
    for x in range(0, 3):
      db_models.PropBet.objects.get(title=data.prop_bet[x].title, 
        league=data.league[0], answer=True)

  def test_league_scoreboard(self):
    data = DataSetup('api_league_scoreboard') 
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

    url = '/api/league/scoreboard'
    request = {'league_name': data.league[0].name}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)

    # invalid league
    request = {'league_name': 'invalid_league'}
    response = {'success': False, 'errors': ['League and user do not match.']}
    self.custom_test(url, request, response, username)
    # not in league
    request = {'league_name': data.league[0].name}
    username = data.user[3].name
    self.custom_test(url, request, response, username)
    # valid
    response = {'scoreboard': [{'username': data.user[0].name, 'score': 3}, 
      {'username': data.user[1].name, 'score': 1}, 
      {'username': data.user[2].name, 'score': 0}], 'success': True}
    username = data.user[0].name
    self.custom_test(url, request, response, username)

  def test_member_admin(self):
    data = DataSetup('api_member_admin') 
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], True)
    data.create_member(data.user[1].get_object(), data.league[0], False)

    url = '/api/member/admin'
    request = {'league_name': data.league[0].name}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)

    # invalid league
    request = {'league_name': 'invalid_league'}
    response = {'success': False, 'errors': ['League and user do not match.']}
    self.custom_test(url, request, response, username)
    # not in league
    request = {'league_name': data.league[0].name}
    username = data.user[2].name
    self.custom_test(url, request, response, username)
    # not admin
    response = {'success': True, 'admin': False}
    username = data.user[1].name  
    self.custom_test(url, request, response, username)
    # valid, picks
    response = {'success': True, 'admin': True}
    username = data.user[0].name  
    self.custom_test(url, request, response, username)

  def test_member_get_picks(self):
    data = DataSetup('api_member_get_picks') 
    data.create_users(3)
    data.create_leagues(2)
    data.create_member(data.user[0].get_object(), data.league[0], False)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_member(data.user[0].get_object(), data.league[1], False)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_pick(data.member[0], data.prop_bet[0], True)
    data.create_pick(data.member[0], data.prop_bet[1], False)
    data.create_pick(data.member[0], data.prop_bet[2], True)

    url = '/api/member/picks/get'
    request = {'league_name': data.league[0].name}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)

    # invalid league
    request = {'league_name': 'invalid_league'}
    response = {'success': False, 'errors': ['League and user do not match.']}
    self.custom_test(url, request, response, username)
    # not in league
    request = {'league_name': data.league[0].name}
    username = data.user[2].name
    self.custom_test(url, request, response, username)
    # valid, no picks & no prop bets
    request = {'league_name': data.league[1].name}
    response = {'success': True, 'picks': {}}
    username = data.user[0].name  
    self.custom_test(url, request, response, username)
    # valid, no picks (returns default False for each prop bet)
    request = {'league_name': data.league[0].name}
    response = {'success': True, 'picks': {data.prop_bet[0].title: False, 
      data.prop_bet[1].title: False, data.prop_bet[2].title: False}}
    username = data.user[1].name  
    self.custom_test(url, request, response, username)
    # valid, picks
    response = {'success': True, 'picks': {data.prop_bet[0].title: True, 
      data.prop_bet[1].title: False, data.prop_bet[2].title: True}}
    username = data.user[0].name  
    self.custom_test(url, request, response, username)

  def test_member_update_picks(self):
    data = DataSetup('api_member_update_picks') 
    data.create_users(2)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)

    url = '/api/member/picks/update'
    request = {'league_name': data.league[0].name, 'picks': 
      {data.prop_bet[0].title: False, data.prop_bet[1].title: False, 
      data.prop_bet[2].title: False}}
    username = data.user[0].name
    self.auth_test(url, request)
    self.parameter_checks(url, request, username)

    # invalid league
    request = {'league_name': 'invalid_league', 'picks': 
      {data.prop_bet[0].title: False, data.prop_bet[1].title: False, 
      data.prop_bet[2].title: False}}
    response = {'success': False, 'errors': ['League and user do not match.']}
    username = data.user[0].name
    self.custom_test(url, request, response, username)
    # not in league
    request = {'league_name': data.league[0].name, 'picks': 
      {data.prop_bet[0].title: False, data.prop_bet[1].title: False, 
      data.prop_bet[2].title: False}}
    username = data.user[1].name
    self.custom_test(url, request, response, username)
    # valid
    response = {'success': True}
    username = data.user[0].name
    self.custom_test(url, request, response, username)
    # check data is updated
    for x in range(0, 3):
      db_models.Pick.objects.get(member=data.member[0], prop_bet=data.prop_bet[x], 
        response=False)       