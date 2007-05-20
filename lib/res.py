import pygame
from pygame.locals import *
from OpenGL.GL import *

class Texture:
  def __init__(self, texturename):
    self.name = texturename
    self.Surface = pygame.image.load('data/gfx/%s.png' % texturename)

    (self.w, self.h) = self.Surface.get_rect()[2:]

    self.glID = glGenTextures(1)
    self.bind()

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,     GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,     GL_CLAMP)

    glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 
                 self.w, self.h,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, 
                 pygame.image.tostring(self.Surface, "RGBA", 0))

  def bind(self):
    glBindTexture(GL_TEXTURE_2D, self.glID)

textures = {}
def getTexture(texturename):
  global textures
  if texturename not in textures:
    textures[texturename] = Texture(texturename)
  return textures[texturename]
