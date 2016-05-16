from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from forms import *
from models import *
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
import json
from django.http import HttpResponseBadRequest
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from decimal import * 
from django.shortcuts import get_object_or_404
from django.db import transaction
import uuid
import time
from random import randint

# Used to generate a one-time-use token to 
from django.contrib.auth.tokens import default_token_generator

#Used to send mail from within Django
from django.core.mail import send_mail

@login_required
def home(request):
  #Set opponent to null
  #Used as a soft reset in case the opponent is not reset at end of multiplayer game
  context = {}
  user = MyUser.objects.get(user=request.user)
  user.opponent = None
  user.queued = False
  user.save()

  context['player'] = user.user.get_username()

  temp = list(user.friends.all())
  friends = []
  for f in temp:
    friends.append(f.user)
  context['friends'] = friends

  context['form'] = SearchForm()
  return render(request,'home.html',context)

@login_required
def getBoard(request):
  context = {}
  players = list(MyUser.objects.order_by('-points')[:20]) #only get top 20 players
  names = []
  for p in players:
    names.append(str(p.user.get_username())+ " - $" + str(p.points))
  jsonD = json.dumps({"players": names})
  if request.method == "GET":
    return HttpResponse(jsonD,content_type='application/json')
  else:
    context['form'] = SearchForm()
    context['player'] = request.user.get_username()
    me = MyUser.objects.get(user=request.user)
    return render(request, "home.html", context)
  
@login_required
def getFam(request):
  context={}
  me = MyUser.objects.get(user=request.user)
  names=[]
  ids=[]
  for f in list(me.friends.all()):
    names.append(f.user.get_username())
    ids.append(f.user.id)
  jsonD = json.dumps({'names':names, 'ids':ids})
  if request.method=='GET':
    return HttpResponse(jsonD, content_type='application/json')
  else:
    context['form'] = SearchForm()
    context['player'] = request.user.get_username()
    me = MyUser.objects.get(user=request.user)

    return render(request, "home.html", context)

@transaction.atomic
def register(request):
  context = {}

  if request.method == 'GET':
    context['form'] = RegistrationForm()
    return render(request,'register.html',context)
  
  form = RegistrationForm(request.POST)
  context['form'] = form

  if not form.is_valid():
    return render(request,'register.html',context)

  new_user = User.objects.create_user(username=form.cleaned_data['user_name'],
                                     password=form.cleaned_data['password1'],
                                    first_name=form.cleaned_data['first_name'],
                                   last_name=form.cleaned_data['last_name'],
                                   email = form.cleaned_data['email'])

  new_user.save()
  inst = MyUser(user = new_user)
    
  inst.save()

  user = authenticate(username=form.cleaned_data['user_name'], 
                    password=form.cleaned_data['password1'])
  login(request,user)
  
  return redirect(reverse('home'))

@login_required
def click(request):
  user = MyUser.objects.get(user=request.user)
  points = user.points + user.mps
  
  user.points = points
  user.save()

  #json = serializers.serialize('json',user.points)
  return HttpResponse(points,content_type='text/plain')

@login_required
def mclick(request):
  user = MyUser.objects.get(user=request.user)
  points = user.mPoints + user.mMps
  
  user.mPoints = points
  user.save()

  #json = serializers.serialize('json',user.points)
  return HttpResponse(points,content_type='text/plain')



#Defines the mps for each item
def getMPS(item):
  if(item == 'yeezy'):
    return 1
  if(item == 'kim'):
    return 10
  if(item == 'tidal'):
    return 100
  if(item == 'gfm'):
    return 1000
  if(item == 'mark'):
    return 10000
#Defines the initial cost to buy each item
def getCost(item):
  if(item == 'yeezy'):
    return 1
  if(item == 'kim'):
    return 10
  if(item == 'tidal'):
    return 100
  if(item == 'gfm'):
    return 1000
  if(item == 'mark'):
    return 10000
#definines the initial cost to buy each debuff
def getDebuffCost(item):
  if(item == 'pirate'):
    return 10
  if(item == 'first'):
    return 10
  if(item == 'second'):
    return 10
  if(item == 'third'):
    return 10
  if(item == 'stop'):
    return 10

#defins the cooldowns for each debuff
def getCooldown(item):
  if(item == 'pirate'):
    return 20
  if(item == 'first'):
    return 10
  if(item == 'second'):
    return 10
  if(item == 'third'):
    return 10
  if(item == 'stop'):
    return 30

@login_required
def bought(request):
  user = MyUser.objects.get(user=request.user)
  id = request.POST['id']
  data = {}
  if(not(id == 'yeezy' or id == 'kim' or id =='tidal' or id =='gfm' or id =='mark')):
    #Invalid items bought, return bad request
    return HttpResponseBadRequest()
  

  #Fetch item, update count 
  try:
    #update item
    owned = Item.objects.get(user=request.user,name=id)
    #check if item can be bought
    if(not(owned.cost <= user.points)):
      return HttpResponse()

    owned.count += 1
    ogCost = owned.cost
    owned.cost = owned.cost * Decimal(1.5) 
    owned.save()
    #update user mps
    user.points = user.points - ogCost
    user.mps += owned.mps
    user.save()
    #send data back to client
    data['id'] = str(id)
    data['mps'] = str(user.mps)
    data['cost'] = str(owned.cost)
    data['money'] = str(user.points)
    data['count'] = str(owned.count)
    jsonD = json.dumps(data)
    return HttpResponse(jsonD,content_type='application/json')

  except ObjectDoesNotExist:
    #create new item
    mpsNew = getMPS(id)
    ogCost = getCost(id)
    costNew = ogCost * 1.5
    #check if item can be bought
    if not(costNew <= user.points):
      return HttpResponse()
    new = Item(name=id,mps=mpsNew,count=1,cost=costNew,user=request.user)
    new.save()
    #update user mps/points
    user.points = user.points - ogCost
    user.mps += new.mps
    user.save() 
    #send data back to client
    data['id'] = str(id)
    data['mps'] = str(user.mps)
    data['cost'] = str(costNew)
    data['money'] = str(user.points)
    data['count'] = '1'
    jsonD = json.dumps(data)
    return HttpResponse(jsonD,content_type='application/json')

#multiplayer buy items handler
@login_required
def mbought(request):
  user = MyUser.objects.get(user=request.user)
  t = int(round(time.time())) - user.time
  
  if((not user.canBuy) and (t >= 20)):#check if users debuff has worn off  
    user.canBuy = True
    user.time = 0
    user.save()
  if(not user.canBuy):
    return HttpResponseBadRequest("debuff " + str(20-t))
  id = request.POST['id']
  data = {}
  if(not(id == 'yeezy' or id == 'kim' or id =='tidal' or id =='gfm' or id =='mark')):
    #Invalid items bought, return bad request
    return HttpResponseBadRequest()
  

  #Fetch item, update count 
  try:
    #update item
    owned = mItem.objects.get(user=request.user,name=id)
    #check if item can be bought
    if(not(owned.cost <= user.mPoints)):
      return HttpResponse()

    owned.count += 1
    ogCost = owned.cost
    owned.cost = owned.cost * Decimal(1.5) 
    owned.save()
    #update user mps
    user.mPoints = user.mPoints - ogCost
    user.mMps += owned.mps
    user.save()
    #send data back to client
    data['id'] = str(id)
    data['mps'] = str(user.mMps)
    data['cost'] = str(owned.cost)
    data['money'] = str(user.mPoints)
    data['count'] = str(owned.count)
    jsonD = json.dumps(data)
    return HttpResponse(jsonD,content_type='application/json')

  except ObjectDoesNotExist:
    #create new item
    mpsNew = getMPS(id)
    ogCost = getCost(id)
    costNew = ogCost * 1.5
    #check if item can be bought
    if not(costNew <= user.mPoints):
      return HttpResponse()
    new = mItem(name=id,mps=mpsNew,count=1,cost=costNew,user=request.user)
    new.save()
    #update user mps/points
    user.mPoints = user.mPoints - ogCost
    user.mMps += new.mps
    user.save() 
    #send data back to client
    data['id'] = str(id)
    data['mps'] = str(user.mMps)
    data['cost'] = str(costNew)
    data['money'] = str(user.mPoints)
    data['count'] = '1'
    jsonD = json.dumps(data)
    return HttpResponse(jsonD,content_type='application/json')

@login_required
def load(request):
    #Send user and corresponding items too client to load initial state
    user = MyUser.objects.get(user=request.user)
    items = Item.objects.filter(user=request.user)
    newL = list(items)
    newL.append(user)
    jsonD = serializers.serialize('json',newL)
    return HttpResponse(jsonD,content_type='application/json')


#increments points by mps for single player
@login_required
def step(request):
  user = MyUser.objects.get(user=request.user)
  user.points += user.mps
  user.save()
  data = {}
  b = user.points >= 53000000 and (not user.won)
  if b:
    user.won = True
    user.save()
  data['money'] = str(user.points)
  data['won'] = str(b)
  return HttpResponse(json.dumps(data),content_type='application/json')

#increments points by mps for multi-player
@login_required
def mstep(request):
  user = MyUser.objects.get(user=request.user)
  t = int(round(time.time())) - user.timeClick 
  if((not user.canClick) and (t >= 30)):#check if users debuff has worn off  
    user.canClick = True
    user.timeClick = 0
    user.save()
  if(not user.canClick):
    return HttpResponseBadRequest('canClick')
  user.mPoints += user.mMps
  user.save()
  data = {}
  data['money'] = str(user.mPoints)
  data['first'] = '0'
  data['second'] = '0'
  data['third'] = '0'
  if(user.first):
    data['first'] = '1'
    user.first = False
    user.save()
  if(user.second):
    data['second'] = '1'
    user.second = False
    user.save()
  if(user.third):
    data['third'] = '1'
    user.third = False
    user.save() 

  return HttpResponse(json.dumps(data),content_type='application/json')

#returns to multiplayer home
@login_required
def mHome(request):
  context={}
  context['form'] = SearchForm()
  context['invite'] = "no"
  return render(request,'mHome.html',context)

@login_required
@transaction.atomic
def queue(request):

  user = MyUser.objects.get(user=request.user)
  if(not user.is_queued()):
    user.queued = True
    user.save()

  #Has existing opponenet
  if(not user.opponent == None):
    return HttpResponse('Found opponenent')
  set = MyUser.objects.filter(queued=True).exclude(user=request.user)
  count = set.count() 
  if(count == 0):
    return HttpResponseBadRequest()

  rando = set[0]
  rando.opponent = user
  user.opponent = rando
  rando.save()
  user.save()
  return HttpResponse('Found opponenent')

@transaction.atomic
@login_required
def ready(request):
  user = MyUser.objects.get(user=request.user)
  user.ready = True
  user.queued = False
  user.save()
  opp = user.opponent
  if(opp.is_ready()):
    return HttpResponse()
  return HttpResponseBadRequest()


#Initialize game with players
@login_required
def game(request):
    context = {}
    context['form'] = SearchForm()
    user = MyUser.objects.get(user=request.user)
    opp = user.opponent
    #temp_opp = User.objects.get(username='test0')
    #opp = MyUser.objects.get(user=temp_opp)
    count = Game.objects.filter(p1=user,p2=opp).count()
    if(count == 0):
      game = Game(p1=user,p2=opp)
      game.save()
    context['opponent'] = opp.user.get_username()
    context['player'] = request.user.get_username()
    return render(request,'game.html',context)

#Initialize game with players
@login_required
def launch(request):
  context = {}
  context['form'] = SearchForm()
  myuser = MyUser.objects.get(user=request.user)
  if(myuser.opponent == None):
    return HttpResponse('Invalid Multiplayer Game')
  context['opponent'] = myuser.opponent.user.get_username()
  context['player'] = request.user.get_username()
  return render(request,'game.html',context)


@login_required
def getopp(request):
  user = MyUser.objects.get(user=request.user)
  opp = user.opponent
  qset = list(MyUser.objects.filter(user = opp.user))
  qset.append(opp.user)
  data = serializers.serialize('json',qset)
  return HttpResponse(data,content_type='application/json')

@transaction.atomic
@login_required
def cancel(request):
  user = MyUser.objects.get(user=request.user)
  user.queued = False
  user.ready = False
  user.save()
  return HttpResponse()

@transaction.atomic
@login_required
def cancel2(request):
  user = MyUser.objects.get(user=request.user)
  game = get_object_or_404(Game,p1=user)
  game.delete()
  return HttpResponse()

@transaction.atomic
@login_required
def link(request):
  
  # Generate a one-time use token for creating html
  user = MyUser.objects.get(user=request.user)
  id = str(uuid.uuid4())
  #delete any existing games that the user is in,although the user should not be inany eixsting games
  filt = Game.objects.filter(p1=user)
  filt2 = Game.objects.filter(p2=user)
  if filt.exists():
    for f in filt:
      f.delete()
  if filt2.exists():
    for f in filt2:
      f.delete()
  #Create new game with unknown p2
  game = Game(uuid=id,p1=user,p2=None)
  game.save()
  link = """ http://%s%s
      """ % (request.get_host(), 
            reverse('invite', args=[id]))
  return HttpResponse(link)

@transaction.atomic
@login_required
def link2(request, id):
  opp = get_object_or_404(User, id=id)

  # Generate a one-time use token for creating html
  user = MyUser.objects.get(user=request.user)

  gid = str(uuid.uuid4())
  game = Game(uuid=gid,p1=user,p2=None)
  game.save()

  link = """ http://%s%s
      """ % (request.get_host(), 
            reverse('invite', args=[gid]))
  email_body = """
  You got invited to play multiplayer.  Please click the link below to
  start saving Pablo:
    %s
  """ % (link)
  send_mail(subject="Invite to play Save Pablo from "+request.user.get_username(),
            message= email_body,
            from_email="nhmu@andrew.cmu.edu",
            recipient_list=[opp.email])
  context={}
  context['invite'] = "yes"
  context['form'] = SearchForm()
  return render(request, "mHome.html", context)

@login_required
@transaction.atomic
def invite(request,id):
  # checks if game was created already, and user is waiting for other to accept
  game = get_object_or_404(Game,uuid=id)
  p2 = MyUser.objects.get(user=request.user)
  #makes sure that the same player does not play themselves
  if (game.p1.user == request.user):
    return HttpResponse("You can't play yourself!")
  p1 = MyUser.objects.get(user = game.p1.user) 
  p1.opponent = p2
  p2.opponent = p1
  p1.save()
  p2.save() 
  game.p2 = p2
  game.save()
  return redirect(reverse('launch'))

@transaction.atomic
@login_required
def waitAccept(request):
  user = MyUser.objects.get(user=request.user)
  game = Game.objects.get(p1=user)

  if(game.p2 == None):
    return HttpResponseBadRequest()

  return HttpResponse()
#helper that reset database values
def unloadHelp(game):
    if game.exists():
      for g in game:
        p1 = g.p1
        p2 = g.p2 
        p1.mPoints = 0
        p1.mMps = 1
        p1.canClick = True
        p1.canBuy = True
        p1.time = 0
        p1.timeClick = 0
        p1.opponent = None
        p2.mPoints = 0
        p2.mMps = 1
        p2.canClick = True
        p2.canBuy = True
        p2.time = 0
        p2.timeClick = 0
        p2.opponent = None 
        p1.save()
        p2.save() 
        items1 = mItem.objects.filter(user=p1.user)
        items2 = mItem.objects.filter(user=p2.user)
        debuff1 = Debuff.objects.filter(user=p1.user)
        debuff2 = Debuff.objects.filter(user=p2.user)
        if items1.exists():
          for item in items1:
            item.delete()
        if items2.exists():
          for item in items2:
            item.delete() 
        if debuff1.exists():
          for item in debuff1:
            item.delete() 
        if debuff2.exists():
          for item in debuff2:
            item.delete() 
        g.delete()

#reset database values when a multiplayer game is finished/terminated
@transaction.atomic
@login_required
def unload(request):
  #extra check 
  myuser = MyUser.objects.get(user=request.user)
  myuser.mPoints = 0
  myuser.mMps = 1
  myuser.save() 
  game = Game.objects.filter(p1=myuser)
  game2 = Game.objects.filter(p2=myuser)
  unloadHelp(game)
  unloadHelp(game2)
  return HttpResponse() 

@login_required
@transaction.atomic
def search(request):
  context = {}
  errors=[]
  form = SearchForm(request.GET)
  context['form'] = form
  
  if not form.is_valid():
    errors.append("Invalid form")
    return render(request,'results.html',context)
  name = form.cleaned_data['username']
  users = User.objects.filter(username__startswith=name)
  if len(list(users)) == 0:
    errors.append("No match for " + name + ". But Kanye still loves Kanye.")
  friends = []
  nonfriends=[]
  me = MyUser.objects.get(user = request.user)
  for u in users:
    if me.friends.filter(user=u):
      friends.append(u)
    else:
      nonfriends.append(u)
  context['friends'] = friends
  context['nonfriends'] = nonfriends
  context['errors'] = errors
  context['me'] = request.user.get_username()
  return render(request, 'results.html', context)


def apply_debuff(request):
  user = MyUser.objects.get(user=request.user)
  opp = user.opponent
  id = request.POST['id']
  if(id == 'pirate'):
    opp.canBuy = False 
    t = int(round(time.time()))
    opp.time = t
    opp.save() 
  elif(id == 'first'): 
    opp.first = True
    opp.mPoints *= Decimal(.8)
    opp.save()
  elif(id == 'second'): 
    opp.second = True
    opp.mMps *= Decimal(.8)
    opp.save()
  elif(id == 'third'):
    rand = randint(1,10)
    if rand <= 8:
      opp.third = True
      stole = opp.mPoints * Decimal(.35)
      opp.mPoints *= Decimal(.65)
      user.mPoints += stole
      opp.save()
      user.save()
    else:
      user.third = True
      stole = user.mPoints * Decimal(.35)
      user.mPoints *= Decimal(.65)
      opp.mPoints += stole
      opp.save()
      user.save()
  elif(id == 'stop'): 
      opp.canClick = False
      opp.timeClick = int(round(time.time()))
      opp.save() 
  return HttpResponse()

#Handles visual updates and logic checks for buying a debuff 
@login_required
def debuff(request):
  user = MyUser.objects.get(user=request.user)
  opp = user.opponent
  id = request.POST['id']
  t = int(round(time.time()))
  data = {}
  if(not(id == 'pirate' or id == 'first' or id =='second' or id =='third' or id =='stop')):
    #Invalid items bought, return bad request
    return HttpResponseBadRequest()
  #get cooldown of item 
  diff = getCooldown(id)
  #Fetch item, update count 
  try:
    #update item
    owned = Debuff.objects.get(user=request.user,name=id)
    #check if item can be bought
    if(not(owned.cost <= user.mPoints) and (t - owned.time >= diff)):
      return HttpResponse()

    ogCost = owned.cost
    owned.cost = owned.cost * Decimal(1.5)
    owned.time = t
    owned.save()
    #update user mps
    user.mPoints = user.mPoints - ogCost
    user.save()
    #send data back to client
    data['id'] = str(id)
    data['cost'] = str(owned.cost)
    data['money'] = str(user.mPoints)
    data['cd'] = str(diff)
    jsonD = json.dumps(data)
    apply_debuff(request)#execute debuff
    return HttpResponse(jsonD,content_type='application/json')

  except ObjectDoesNotExist:
    #create new item
    ogCost = getDebuffCost(id)
    costNew = ogCost * 1.5
    #check if item can be bought
    if not(ogCost <= user.mPoints):
      return HttpResponse()
    new = Debuff(name=id,cost=costNew,user=request.user,time=t)
    new.save()
    #update user points
    user.mPoints = user.mPoints - ogCost
    user.save() 
    #send data back to client
    data['id'] = str(id)
    data['cost'] = str(costNew)
    data['money'] = str(user.mPoints)
    data['cd'] = str(diff)
    jsonD = json.dumps(data)
    apply_debuff(request)#execute debuff
    return HttpResponse(jsonD,content_type='application/json')

@login_required
@transaction.atomic
def friend(request, id):
  context={}
  me = MyUser.objects.get(user=request.user)
  context['player'] = me.user.get_username()

  friend = User.objects.get(id=id)
  add = get_object_or_404(MyUser, user=friend)
  me.friends.add(add)
  me.save()
  temp = me.friends.all()
  friends = []
  for f in list(temp):
    friends.append(f.user)
  context['friends'] = friends
  context['form'] = SearchForm()
  add.friends.add(me)
  return render(request, "home.html", context)

@login_required
@transaction.atomic
def unfriend(request, id):
  context={}
  me = MyUser.objects.get(user=request.user)
  context['player'] = me.user.get_username()

  friend = User.objects.get(id=id)
  remove = get_object_or_404(MyUser, user=friend)
  me.friends.remove(remove)
  me.save()
  temp = me.friends.all()
  friends = []
  for f in list(temp):
    friends.append(f.user)
  context['friends'] = friends
  context['form'] = SearchForm()
  remove.friends.remove(me)
  return render(request, "home.html", context)

@login_required
def congrats(request):
  context = {}
  context['form'] = SearchForm()
  context['player'] = request.user.get_username()
  return render(request, "celebration.html", context)

@login_required
def lose(request):
  context={}
  context['form'] = SearchForm()
  context['player'] = request.user.get_username()
  return render(request, "lose.html", context)
