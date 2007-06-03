from sprite import *
from timing import timer
import random
import res

def sign(x):
  if x < 0:
    return -1
  else:
    return 1

class enemy(Sprite):
  def __init__(self, enemyname):
    Sprite.__init__(self, enemyname)
    self.health = 100
    self.state = 'normal'
    self.nextstate = -1
    self.ice = False
    self.damager = None

    self.nextAiState = 0
    self.aiState = 'walking'

    self.aiStateTraversals = \
      {'walking': [('walking', i/3 + 1) for i in range(10)] + [('jumping', 0), ('standing', 1), ('turnAround', 0)],
       'jumping': [('walking', 5)],
       'ranAgainstWallRight': [('walkBackLeft', 0.75)],
       'ranAgainstWallLeft':  [('walkBackRight',0.75)],
       'walkBackLeft':  [('jumpBack', 0), ('walking', 1)],
       'walkBackRight': [('jumpBack', 0), ('walking', 1)],
       'jumpBack': [('jumping', 0)],
       'turnAround': [('walking', 1)],
       'standing': [('walking', 5), ('standing', 1)],
      }

  def doWhatAiTellsYouTo(self):
    if self.nextAiState <= 0:
      (self.aiState, self.nextAiState) = random.choice(self.aiStateTraversals[self.aiState])
      if self.nextAiState != 0:
        self.nextAiState += random.random()
    self.nextAiState -= timer.curspd

    if self.aiState == 'walking':
      self.vx += sign(self.vx) * (1.0 - abs(self.vx)) * timer.curspd
    elif self.aiState == 'jumping':
      if self.physics == "standing":
        self.vy -= 4
    elif self.aiState == "walkBackLeft":
      self.vx = min(max(-1, self.vx - timer.curspd), 0)
    elif self.aiState == "walkBackRight":
      self.vx = max(min(1, self.vx + timer.curspd), 0)
    elif self.aiState == "jumpBack":
      if self.physics == "standing":
        self.vx *= -1
        self.vy -= 4
    elif self.aiState == "turnAround":
      self.vx *= -1
    elif self.aiState == "standing":
      self.vx *= 0.95
    else:
      self.nextAiState = 0

  def hitLeft(self):
    self.aiState = "ranAgainstWallLeft"
    self.nextAiState = 0

  def hitRight(self):
    self.aiState = "ranAgainstWallRight"
    self.nextAiState = 0

  def draw(self, image = None):
    if self.state == 'ouch' and timer.blink(0.1):
      Sprite.draw(self, image, 0.5)
    else:
      Sprite.draw(self, image)
    if self.state == 'frozen' and not self.ice:
      self.ice = True
      self.draw(res.getTexture("iceblock"))
      self.ice = False

  def setstate(self, state, duration = -1):
    self.state = state
    self.nextstate = duration
    if state in ['normal', 'paralysed', 'burning'] and self.health > 0:
      self.damager.damage = 1
    else:
      self.damager.damage = 0
      if self.health <= 0 and state not in ['dead', 'ouch']:
        self.damager.lifetime = 0
        self.setstate('dead')

  def move(self):
    if self.state == 'frozen':
      if self.vy < -0.1:
        self.vx *= 0.99
        self.vy *= 0.999
      else:
        self.vy = -5 * timer.curspd
        self.vx = 0
    elif self.state == 'twisting':
      self.vx = random.random()
    elif self.state == 'paralysed':
      self.vx *= 0.9
    Sprite.move(self)
    (self.damager.x, self.damager.y) = (self.x, self.y)
    (self.damager.vx, self.damager.vy) = (self.vx, self.vy)

    self.doWhatAiTellsYouTo()

    if self.nextstate != -1:
      self.nextstate -= timer.curspd
      if self.nextstate < 0:
        if self.state in ['normal', 'ouch', 'twisting', 'drowning', 'burning', 'paralysed']:
          if self.health < 0:
            self.setstate('dead')
          else:
            self.setstate('normal')
          self.nextstate = -1
        elif self.state == 'frozen':
          self.health = -1
          self.setstate('ouch', 0.25)
          self.vy = random.random() * -4
          self.vx = random.random() * 4 - 2
