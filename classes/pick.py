# -*- coding: utf-8 -*-

import ui.models as db_models
import classes.user
import classes.league
import classes.member
import classes.prop_bet

class Pick:
  '''Corresponds to one Member's response to a given PropBet in a League.'''
  def __init__(self, user_name, league_name, prop_bet_title):
    self.user_name = user_name
    self.league_name = league_name
    self.prop_bet_title = prop_bet_title
    self.user_object = None
    self.league_object = None
    self.member_object = None
    self.prop_bet_object = None
    # stores the corresponding object from the Django ORM
    self.db_object = None
  def __repr__(self):
    return "Pick(user_name=%r, league_name=%r, prop_bet_title=%r)" % (
      self.user_name, self.league_name, self.prop_bet_title)
  def __str__(self):
    return "{'user_name': %r, 'league_name': %r, 'prop_bet_title': %r}" % (
      self.user_name, self.league_name, self.prop_bet_title)
  def __eq__(self, other):
    if isinstance(other, Pick):
      return (self.user_name == other.user_name and 
        self.league_name == other.league_name and 
        self.prop_bet_title == other.prop_bet_title)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash((self.user_name, self.league_name, self.prop_bet_title))
  def _lookup_user(self):
    self.user_object = classes.user.User(self.user_name).get_object()
  def _lookup_league(self):
    self.league_object = classes.league.League(self.league_name).get_object()
  def _lookup_member(self):
    self.member_object = classes.member.Member(self.user_name, self.league_name
      ).get_object()
  def _lookup_prop_bet(self):
    self.prop_bet_object = classes.prop_bet.PropBet(self.prop_bet_title, 
      self.league_name).get_object()   
  def lookup(self):
    self._lookup_member()
    self._lookup_prop_bet()
    self.db_object = db_models.Pick.objects.filter(member=self.member_object, 
      prop_bet=self.prop_bet_object)
    if len(self.db_object) != 1:
      self.db_object = None
    else:
      self.db_object = self.db_object[0]
    return self
  def create_or_update(self, response):
    self.lookup()
    if self.db_object:
      self.db_object.response = response
      self.db_object.save()
      return True
    else:
      self._lookup_member()
      self._lookup_prop_bet()
      if self.member_object and self.prop_bet_object:
        self.db_object = db_models.Pick(member=self.member_object, 
          prop_bet=self.prop_bet_object, response=response)
        self.db_object.save()
        return True
      else:  
        return False
  def get_user_name(self):
    return self.user_name
  def get_league_name(self):
    return self.league_name
  def get_prop_bet_title(self):
    return self.prop_bet_title 
  def get_user_object(self):
    if not self.user_object:
      self._lookup_user()
    return self.user_object
  def get_league_object(self):
    if not self.league_object:
      self._lookup_league()
    return self.league_object
  def get_member_object(self):
    if not self.member_object:
      self._lookup_member()
    return self.member_object
  def get_prop_bet_object(self):
    if not self.prop_bet_object:
      self._lookup_prop_bet()
    return self.prop_bet_object 
  def get_object(self):
    if not self.db_object:
      self.lookup()
    return self.db_object  