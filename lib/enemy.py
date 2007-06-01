from sprite import *
from timing import timer
import random
import res

class enemy(Sprite):
  def __init__(self, enemyname):
    Sprite.__init__(self, enemyname)
    self.health = 100
    self.state = 'normal'
    self.nextstate = -1
    self.ice = False
    self.damager = None

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
