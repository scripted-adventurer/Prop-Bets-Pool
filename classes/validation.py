# -*- coding: utf-8 -*-

import hashlib
import ui.models as db_models
import classes.league

class Validation:
  '''Conducts repeatable validation tests, returning True or False accordingly.'''
  def __init__(self):
    pass
  def unique_league_name(self, league_name):
    if len(db_models.League.objects.filter(name=league_name)) == 0:
      return True
    else:
      return False
  def league_password_correct(self, league_name, league_password):
    league = classes.league.League().get_object(league_name)
    if league and (hashlib.sha256(league_password.encode('utf-8')).hexdigest() == 
      league.password):
      return True
    else:
      return False
  def prop_bet_exists(self, title, league_name):
    league = classes.league.League().get_object(league_name)
    if len(db_models.PropBet.objects.filter(title=title, league=league)) != 0:
      return True
    else:
      return False
  def user_is_member(self, user_object, league_name):
    league = classes.league.League().get_object(league_name)
    if len(db_models.Member.objects.filter(user=user_object, league=league)) != 0:
      return True
    else:
      return False
  def user_is_admin(self, user_object, league_name):
    league = classes.league.League().get_object(league_name)
    if len(db_models.Member.objects.filter(user=user_object, league=league, 
      admin=True)) != 0:
      return True
    else:
      return False      