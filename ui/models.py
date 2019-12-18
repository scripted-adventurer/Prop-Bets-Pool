# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models

class League(models.Model):
  name = models.TextField()
  # league password is stored as SHA256 hash
  password = models.TextField()

class Member(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  league = models.ForeignKey(League, on_delete=models.CASCADE)
  admin = models.BooleanField(default=False)

class PropBet(models.Model):
  league = models.ForeignKey(League, on_delete=models.CASCADE)
  title = models.TextField()
  answer = models.BooleanField(null=True)

class Pick(models.Model):
  member = models.ForeignKey(Member, on_delete=models.CASCADE)
  prop_bet = models.ForeignKey(PropBet, on_delete=models.CASCADE)
  response = models.BooleanField(null=True)
