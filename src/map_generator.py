from PIL import Image, ImageDraw, ImageFont
import random

# TODO add lifespan?
class Species:
  def __init__(self, rad, rad_var, rad_ecc, color, color_var):
    self.rad, self.rad_var, self.rad_ecc, self.color, self.color_var = rad, rad_var, rad_ecc, color, color_var

class Tree:
  def __init__(self, species):
    rad_var = random.randint(-species.rad_var, species.rad_var)
    self.x_rad = species.rad + rad_var + vary(species.rad_ecc)
    self.y_rad = species.rad + rad_var + vary(species.rad_ecc)
    r,g,b = species.color
    rv, gv, bv = species.color_var
    self.color = r+vary(rv), g+vary(gv), b+vary(bv)

def vary(x):
  return random.randint(-x,x)

def build_forest(params={}):
  sx,sy = size = params.get("size", (5000,5000))
  density = params.get("density", 1)
  grass_color = (75,255,75)
  out = Image.new("RGB", size, grass_color)
  d = ImageDraw.Draw(out)
  # We maintain a map of buckets, each containing some trees, a list of (x,y,species_ix, remaining_lifespan). This makes it faster to check for collisions.
  bucket_length = 100
  buckets = {(xb,yb):[] for xb in range(sx//bucket_length+1) for yb in range(sy//bucket_length+1)} # bucket coords to list of tree coords
  trees = dict() # tree coords to tree data
  # Initialise with a few different species of tree.
  num_species = 5
  species_data = [Species(40+5*i, 5, 2, (20+4*i+200*(i==3), 150, 5*i), (5,5,5)) for i in range(num_species)]
  # add trees
  for i in range(int(density*sx*sy/10000)):
    species = random.choice(species_data)
    new_tree = Tree(species)
    px, py = random.randint(0,sx), random.randint(0,sy)
    xb, yb = px // bucket_length, py // bucket_length
    # confirm it can spawn there: is it within bounds; and for its new bucket pom 1 in each drn, there's nothing where dist (t, new_t) < t.rad + new_t.rad; and if I later add streams, it's not inside one
    overlaps = [(xo,yo) for x in {max(0,xb-1),xb,min(sx//bucket_length,xb+1)} for y in {max(0,yb-1),yb,min(sy//bucket_length,yb+1)} for xo,yo in buckets[(x,y)] if is_overlap(new_tree,px,py,trees[(xo,yo)], xo,yo)]
    if not overlaps:
      trees[(px, py)] = new_tree
      buckets[(xb, yb)] += [(px, py)]

  for ((x,y),tree) in trees.items():
    d.ellipse([(x-tree.x_rad, y-tree.y_rad), (x+tree.x_rad, y+tree.y_rad)], fill=tree.color)
  
  out.show()
  
def is_overlap(t1, x1,y1, t2, x2,y2):
  return 2*(x1-x2)**2 + (y1-y2)**2 < (t1.x_rad + t2.x_rad)**2 + (t1.y_rad + t2.y_rad)**2

if __name__=="__main__":
  build_forest()