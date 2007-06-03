import pygame
from pygame.locals import *
from OpenGL.GL import *
import font, timing

class Area:
  def __init__(self, rect):
    self.rect = rect
    self.children = []

  def takeFocus(self, clickPos):
    """checks if the click hit the area. check sub-areas first.
the area that got hit returns self and the return value gets returned to the
original caller."""
    for ch in self.children:
      rv = ch.takeFocus(clickPos)
      if rv:
        return rv

    if self.rect.collidepoint(*clickPos):
      return self

    return None

  def handleEvent(self, event):
    pass

  def draw(self):
    pass

  def focusReceived(self):
    self.focus = True
  
  def focusLost(self):
    self.focus = False

  def deleteMe(self):
    return False

class MessagePopup(Area):
  def __init__(self, text, duration):
    self.startTime = timing.timer.now()
    self.endTime = self.startTime + duration
    self.font = font.Text(text)

    self.children = []

    self.rect = pygame.Rect(0, 0, self.font.w, self.font.h)
    self.rect.center = pygame.display.get_surface().get_rect().center

  def draw(self):
    glDisable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(self.rect.x / 32, self.rect.y / 32, 0)
    if self.endTime - timing.timer.now() < 1:
      t = self.endTime - timing.timer.now()
      glScalef(t, t, 1)
    glBegin(GL_QUADS)
    glColor4f(1, 0, 0, 0.75)
    glVertex2f(-0.5,                     -0.5)
    glVertex2f(-0.5,                      0.5 + self.rect.h / 32.)
    glVertex2f( 0.5 + self.rect.w / 32.,  0.5 + self.rect.h / 32.)
    glVertex2f( 0.5 + self.rect.w / 32., -0.5 + 0)
    glEnd()
    glScalef(32 ** -1, 32 ** -1, 1)
    self.font.draw()
    glPopMatrix()

  def deleteMe(self):
    return timing.timer.now() >= self.endTime

class TextInputArea(Area):
  def __init__(self, text, rect, prompt=""):
    self.font = font.Text(prompt + text)
    self.text = text
    self.rect = rect
    self.prompt = prompt
    self.children = []
    self.focus = False

  def handleEvent(self, ev):
    if ev.type == KEYDOWN:
      if ev.key not in [K_RETURN, K_BACKSPACE]:
        if ev.unicode:
          self.text += ev.unicode
          self.refreshFont()
      elif ev.key == K_BACKSPACE:
        self.text = self.text[:-1]
        self.refreshFont()
      elif ev.key == K_RETURN:
        self.inputDone()
    else:
      return ev

  def draw(self):
    glPushMatrix()
    glTranslatef(self.rect.x / 32., self.rect.y / 32., 0)
    glScalef(32 ** -1, 32 ** -1, 1)
    self.font.draw()
    glPopMatrix()

  def refreshFont(self):
    if self.focus:
      self.font.renderText(self.prompt + self.text + "_")
    else:
      self.font.renderText(self.prompt + self.text)

  def focusReceived(self):
    self.focus = True
    self.refreshFont()

  def focusLost(self):
    self.focus = False
    self.refreshFont()

  def setText(self, text):
    self.text = text
    self.refreshFont()

areas = []
curfoc = None
def popup(text):
  global areas
  areas.append(MessagePopup(text, 10))

def handleEvent(ev):
  global areas, curfoc
  if ev.type == MOUSEBUTTONDOWN:
    oldfoc = curfoc
    # check for new focus
    for ar in areas:
      curfoc = ar.takeFocus(ev.pos) or curfoc
    if oldfoc != curfoc:
      if oldfoc:
        oldfoc.focusLost()
      if curfoc:
        curfoc.focusReceived()

  if not curfoc or curfoc.handleEvent(ev):
    # we may have a globally accepted event here
    for ar in areas:
      # loop until someone accepts the event
      if not ar.handleEvent(ev):
        break

def draw():
  global areas
  for ar in areas:
    ar.draw()
    if ar.deleteMe():
      areas.remove(ar)
