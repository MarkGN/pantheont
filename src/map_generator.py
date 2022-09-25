from PIL import Image, ImageDraw, ImageFont
import random

def build_forest(params={}):
  size = params.get("size", (1000,1000))
  grass_color = (75,255,75)
  tree_color = (30,150,0)
  out = Image.new("RGB", size, grass_color)
  d = ImageDraw.Draw(out)
  # Initialise with 3 different species of tree.
  
  d.ellipse([(0,0),(100,100)], fill=tree_color, outline=None, width=1)
  d.ellipse([(300,200),(400,300)], fill=tree_color, outline=None, width=1)
  d.ellipse([(100,400),(200,500)], fill=tree_color, outline=None, width=1)
  out.show()
  return NotImplementedError

if __name__=="__main__":
  build_forest()