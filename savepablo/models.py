from django.db import models

# User class for built-in authentication module
from django.contrib.auth.models import User

class MyUser(models.Model):
  user = models.OneToOneField(User)
  points = models.DecimalField(max_digits=11,decimal_places=0, default=0)
  friends = models.ManyToManyField("self",symmetrical=True)
  mps = models.DecimalField(max_digits=100,decimal_places=1,default=1)
  queued = models.BooleanField(default=0)
  opponent = models.OneToOneField("self",null=True,blank=True,default=None)
  ready = models.BooleanField(default=0)
  mPoints = models.DecimalField(max_digits=11,decimal_places=0, default=0)
  mMps = models.DecimalField(max_digits=100,decimal_places=1,default=1)
  canBuy = models.BooleanField(default=1)
  time = models.IntegerField(default=0)
  canClick = models.BooleanField(default=1)
  timeClick = models.IntegerField(default=0)
  first = models.BooleanField(default = 0)
  second = models.BooleanField(default = 0)
  third = models.BooleanField(default = 0)
  won = models.BooleanField(default = 0)




  #queued by default returns an integer value, easier to convert to a bool 
  def is_queued(self):
    return bool(self.queued)
  def is_ready(self):
    return bool(self.ready)
  def __unicode__(self):
  	return self.user.username
  def __str__(self):
  	return self.__unicode__()
  

class Item(models.Model):
  name = models.CharField(max_length = 20)
  mps = models.DecimalField(max_digits=100,decimal_places=2,default=0)
  count = models.IntegerField()
  cost = models.DecimalField(max_digits=100,decimal_places=2,default=0)
  user = models.ForeignKey(User)

  def __unicode__(self):
    return self.user.username

  def __str__(self):
    return self.__unicode__()

class mItem(models.Model):
  name = models.CharField(max_length = 20)
  mps = models.DecimalField(max_digits=100,decimal_places=2,default=0)
  count = models.IntegerField()
  cost = models.DecimalField(max_digits=100,decimal_places=2,default=0)
  user = models.ForeignKey(User)

  def __unicode__(self):
    return self.user.username

  def __str__(self):
    return self.__unicode__()


class Game(models.Model):
  uuid = models.CharField(max_length = 100,default='0')
  p1 = models.OneToOneField(MyUser,related_name='+',default = None,null=True)
  p2 = models.OneToOneField(MyUser,related_name='+',default = None,null=True)

class Debuff(models.Model):
  name = models.CharField(max_length = 20)
  cost = models.DecimalField(max_digits=100,decimal_places=1,default=0)
  user = models.ForeignKey(User)
  time = models.IntegerField(default = 0) 

