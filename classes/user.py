# -*- coding: utf-8 -*-

from django.contrib.auth.models import User as Auth_User
import ui.models as db_models

class User:
  '''Represents a single person's unique identity used across leagues. Can have
  many associated Members, one for each League the user has joined. Primarily
  wraps the built in Django User object.'''
  def __init__(self, name):
    self.name = name
    # stores the corresponding object from the Django ORM
    self.db_object = None
  def __repr__(self):
    return "User(name=%r)" % (self.name)
  def __str__(self):
    return self.name
  def __eq__(self, other):
    if isinstance(other, User):
      return self.name == other.name
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(self.name)
  def create(self, password, email=''):
    self.db_object = Auth_User.objects.create_user(self.name, email, password)
    return self
  def lookup(self):
    self.db_object = Auth_User.objects.filter(username=self.name)
    if len(self.db_object) != 1:
      self.db_object = None
    else:
      self.db_object = self.db_object[0]
    return self  
  def delete(self):
    if not self.db_object:
      self.lookup()
    if self.db_object:
      self.db_object.delete()
      return True
    else:
      return False   
  def get_leagues(self):
    # returns a list of League objects the user is a member of
    if not self.db_object:
      self.lookup()
    members = db_models.Member.objects.filter(user=self.db_object)
    return [row.league.name for row in members]   
  def get_name(self):
    return self.name
  def get_object(self):
    if not self.db_object:
      self.lookup()
    return self.db_object     