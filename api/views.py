# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token

import classes.user
import classes.league
import classes.member
import classes.pick
import classes.prop_bet

def login_required(view_func):
  # a custom version based on the Django built in that checks for authentication
  # and returns an HTTP 401 with an error message if check fails
  @wraps(view_func)
  def wrapper(request, *args, **kwargs):
    if not request.user.is_authenticated:
      response = {'success': False, 'errors': 
        ['Authentication required.']}
      return JsonResponse(response, status=401)
    else:
      return view_func(request, *args, **kwargs)
  return wrapper

class InputValidation:
  def __init__(self, request, required_params=[]):
    self.request_data = json.loads(request.body)
    self.user = request.user
    self.success = True
    self.errors = []
    for param in required_params:
      if param not in self.request_data or not self.request_data[param]:
        self.errors.append('Missing or invalid data for %s' % param)
        self.success = False
    if not self.success:
      self.http_status = 400
    else:
      self.http_status = 200
    self.response_data = {}
  def add_response_data(self, response_data):
    for key, value in response_data.items():
      self.response_data[key] = value
  def add_error(self, error):
    self.errors.append(error)
    self.success = False
  def create_output_json(self):
    if self.errors:
      self.response_data['errors'] = self.errors
    self.response_data['success'] = self.success
    return JsonResponse(self.response_data, status=self.http_status)          

def main(request):
  return render(request, 'api/base.html')

def signup(request):
  required_params = ['username', 'password1', 'password2']
  validation = InputValidation(request, required_params)
  if validation.success:
    username = validation.request_data['username']
    user = classes.user.User(username)
    email = validation.request_data['email']
    password1 = validation.request_data['password1']
    password2 = validation.request_data['password2']
    if password1 != password2:
      validation.add_error('Passwords do not match.')
    elif user.get_object():
      validation.add_error('Username is already taken.')
    else:
      user.create(password=password1, email=email)
  return validation.create_output_json() 

def login_user(request):
  required_params = ['username', 'password']
  validation = InputValidation(request, required_params)
  if validation.success:
    username = validation.request_data['username']
    password = validation.request_data['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      new_csrf = get_token(request)
      validation.add_response_data({'csrf_token': new_csrf})
    else:
      validation.add_error('Username and/or password is incorrect.')
  return validation.create_output_json()

def logout_user(request):
  validation = InputValidation(request)
  if validation.success:
    logout(request)
  return validation.create_output_json()  

@login_required
def user_leagues(request):
  validation = InputValidation(request)
  if validation.success:
    user = request.user
    response_data = {}
    response_data['leagues'] = classes.user.User(user.username).get_leagues()
    validation.add_response_data(response_data)
  return validation.create_output_json()

@login_required
def league_create(request):
  required_params = ['league_name', 'password', 'prop_bets']
  validation = InputValidation(request, required_params)
  if validation.success:
    user = request.user
    league_name = validation.request_data['league_name']
    league = classes.league.League(league_name)
    password = validation.request_data['password']
    prop_bets = validation.request_data['prop_bets'].split('\n')

    if not league.unique_name():
      validation.add_error('League name is taken.')
    else:  
      success = league.create(user, password, prop_bets)
      if not success:
        validation.add_error('Unable to create new league.')
  return validation.create_output_json()

@login_required
def league_join(request):
  required_params = ['league_name', 'password']
  validation = InputValidation(request, required_params)
  if validation.success:
    user = request.user
    league_name = validation.request_data['league_name']
    password = validation.request_data['password']
    league = classes.league.League(league_name)
    member = classes.member.Member(user.username, league_name)

    if not league.correct_password(password):
      validation.add_error('League name and password do not match.')
    else:  
      success = member.create(admin=False)
      if not success:
        validation.add_error('Unable to join league.')
  return validation.create_output_json()

@login_required
def league_prop_bets(request):
  required_params = ['league_name']
  validation = InputValidation(request, required_params)
  if validation.success:
    user = request.user
    league_name = validation.request_data['league_name']
    league = classes.league.League(league_name)
    member = classes.member.Member(user.username, league_name)

    if not member.is_member():
      validation.add_error('League and user do not match.')
    else:  
      response_data = {}
      response_data['prop_bets'] = league.get_prop_bets()
      validation.add_response_data(response_data)
  return validation.create_output_json()

@login_required
def league_answers(request):
  required_params = ['league_name', 'answers']
  validation = InputValidation(request, required_params)
  if validation.success:
    user = request.user
    league_name = validation.request_data['league_name']
    answers = validation.request_data['answers']
    league = classes.league.League(league_name)
    member = classes.member.Member(user.username, league_name)

    if not member.is_admin():
      validation.add_error('League and user do not match (user must be admin).')
    else:  
      success = league.update_answers(answers)
      if not success:
        validation.add_error('Unable to update league answers.')
  return validation.create_output_json()

@login_required
def league_scoreboard(request):
  required_params = ['league_name']
  validation = InputValidation(request, required_params)
  if validation.success:
    user = request.user
    league_name = validation.request_data['league_name']
    league = classes.league.League(league_name)
    member = classes.member.Member(user.username, league_name)

    if not member.is_member():
      validation.add_error('League and user do not match.')
    else:  
      response_data = {}
      response_data['scoreboard'] = league.get_scoreboard()
      validation.add_response_data(response_data)
  return validation.create_output_json()

@login_required
def member_admin(request):
  required_params = ['league_name']
  validation = InputValidation(request, required_params)
  if validation.success:
    user = request.user
    league_name = validation.request_data['league_name']
    member = classes.member.Member(user.username, league_name)

    if not member.is_member():
      validation.add_error('League and user do not match.')
    else:  
      response_data = {}
      response_data['admin'] = member.is_admin()
      validation.add_response_data(response_data)
  return validation.create_output_json()  

@login_required
def member_get_picks(request):
  required_params = ['league_name']
  validation = InputValidation(request, required_params)
  if validation.success:
    user = request.user
    league_name = validation.request_data['league_name']
    league = classes.league.League(league_name)
    member = classes.member.Member(user.username, league_name)

    if not member.is_member():
      validation.add_error('League and user do not match.')
    else:  
      prop_bets = league.get_prop_bets()
      existing_picks = member.get_picks()
      all_picks = {}
      for prop_bet in prop_bets.keys():
        if prop_bet in existing_picks:
          all_picks[prop_bet] = existing_picks[prop_bet]
        else:
          all_picks[prop_bet] = False
      response_data = {}
      response_data['picks'] = all_picks
      validation.add_response_data(response_data)
  return validation.create_output_json()

@login_required
def member_update_picks(request):
  required_params = ['league_name', 'picks']
  validation = InputValidation(request, required_params)
  if validation.success:
    user = request.user
    league_name = validation.request_data['league_name']
    picks = validation.request_data['picks']
    member = classes.member.Member(user.username, league_name)

    if not member.is_member():
      validation.add_error('League and user do not match.')
    else:  
      success = member.update_picks(picks)
      if not success:
        validation.add_error('Unable to update picks.')
  return validation.create_output_json()            