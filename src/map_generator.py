import base64
import io
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Point, Polygon
import math, random, simplejson

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

# Of two trees
def is_overlap(t1, x1,y1, t2, x2,y2, margin=1):
  return (x1-x2)**2 + (y1-y2)**2 < margin*( (t1.x_rad + t2.x_rad)**2 + (t1.y_rad + t2.y_rad)**2)

# Of a tree in a river
def is_in_river(px, py, river):
  point = Point((px, py))
  polygon = Polygon(river)
  return polygon.contains(point)

#TODO add parameters
#TODO This is a lousy algorithm: the stream can self-intersect.
# For these parameters, it usually doesn't, but I should rewrite so that it can't.
def build_river(params={}):
  w = params.get("map-width", 100)
  seg_length = 60
  seg_meander = 0.5
  n_sgs = 50
  width = 90
  width_var = 30
  px,py = 0,random.randint(0,w)
  drn = 0
  pts, rev_pts = [None for i in range(n_sgs)], [None for i in range(n_sgs)]
  for i in range(n_sgs):
    wl = width+vary(width_var)
    pts[i] = (int(px-wl*math.sin(drn)), int(py+wl*math.cos(drn)))
    wl = width+vary(width_var)
    rev_pts[i] = (int(px+wl*math.sin(drn)), int(py-wl*math.cos(drn)))
    px += seg_length*math.cos(drn)
    py += seg_length*math.sin(drn)
    drn += seg_meander*(2*random.random()-1)
  rev_pts.reverse()
  return pts + rev_pts

# TODO factor stuff out, like creating trees
# TODO So this is pretty cool, but it'd be nice to be able to say:
# 1) I want grass, trees;
# 2) I want a clearing, maybe even with some traveller bedrolls;
# 3) I want a stream, which might even branch
# ... and it'd be nice to wrap it in a separate function creating multiple terrains,
# so that eg I could have a cave system
# ... How would a cave look? These dense forests are open-ish, in that you can go in many directions but it's always hard going; a cave has a limited number of routes.
# Maybe have multiple rooms, with twisting corridors between? How? Just have one or two bends? Plus maybe the odd dead end?
def build_forest(params={}):
  sx,sy = size = params.get("size", (500,500))
  density = params.get("density", 1)
  tree_thickness = params.get("tree-thick")
  grass_color = (75,255,55)
  brown = (130, 130, 0)
  out = Image.new("RGB", size, brown)
  d = ImageDraw.Draw(out)
  border = 10
  d.rectangle([(border, border), (sx-border,sy-border)], fill=grass_color)
  # d.rectangle()
  line_of_sight = []
  ppg = params.get("pix",1) # pixels per grid unit
  oosqrt2 = 2**-0.5
  # We maintain a map of buckets, each containing some trees, a list of (x,y,species_ix, remaining_lifespan). This makes it faster to check for collisions.
  bucket_length = 100
  buckets = {(xb,yb):[] for xb in range(sx//bucket_length+1) for yb in range(sy//bucket_length+1)} # bucket coords to list of tree coords
  trees = dict() # tree coords to tree data
  # Initialise with a few different species of tree.
  num_species = 2
  species_data = [Species(80+50*i, 5+5*i, 5, (30, 150, 10), (20,40,5)) for i in range(num_species)]
  # add trees
  for i in range(int(density*sx*sy/10000)):
    species = random.choice(species_data)
    new_tree = Tree(species)
    px, py = random.randint(0,sx), random.randint(0,sy)
    xb, yb = px // bucket_length, py // bucket_length
    # confirm it can spawn there: is it within bounds; and for its new bucket pom 1 in each drn, there's nothing where dist (t, new_t) < t.rad + new_t.rad; and if I later add streams, it's not inside one
    overlaps = [(xo,yo) for x in {max(0,xb-1),xb,min(sx//bucket_length,xb+1)} for y in {max(0,yb-1),yb,min(sy//bucket_length,yb+1)} for xo,yo in buckets[(x,y)] if is_overlap(new_tree,px,py,trees[(xo,yo)], xo,yo, margin=tree_thickness)]
    if not overlaps:
      trees[(px, py)] = new_tree
      buckets[(xb, yb)] += [(px, py)]

  # add a clearing
  x,y = random.randint(2,sx//bucket_length-2),random.randint(2,sy//bucket_length-2)
  for x1 in range(x-2,x+3):
    for y1 in range(y-2, y+3):
      for coord in buckets[x1,y1]:
        del trees[coord]

  # add a river
  river = build_river({"map-width":sx})
  d.polygon(river, fill=(0,0,255), outline=(0,0,0))
  trees = {(px,py):value for (px,py),value in trees.items() if not is_in_river(px,py,river)}

  for ((x,y),tree) in trees.items():
    d.ellipse([(x-tree.x_rad, y-tree.y_rad), (x+tree.x_rad, y+tree.y_rad)], fill=tree.color, outline=(0,0,0))
    line_of_sight.append([{"x":(x-tree.x_rad*oosqrt2)/ppg, "y":(y-tree.y_rad*oosqrt2)/ppg},{"x":(x+tree.x_rad*oosqrt2)/ppg, "y":(y+tree.y_rad*oosqrt2)/ppg},{"x":(x-tree.x_rad*oosqrt2)/ppg, "y":(y-tree.y_rad*oosqrt2)/ppg}])
    line_of_sight.append([{"x":(x-tree.x_rad*oosqrt2)/ppg, "y":(y+tree.y_rad*oosqrt2)/ppg},{"x":(x+tree.x_rad*oosqrt2)/ppg, "y":(y-tree.y_rad*oosqrt2)/ppg},{"x":(x-tree.x_rad*oosqrt2)/ppg, "y":(y+tree.y_rad*oosqrt2)/ppg}])
  line_of_sight.append([{"x":0,"y":0},{"x":0,"y":sy/ppg},{"x":sx/ppg,"y":sy/ppg},{"x":sx/ppg,"y":0},{"x":0,"y":0}])

  return out, line_of_sight

if __name__=="__main__":
  ppg = 50
  width = 2500
  image, los = build_forest(params={"size":(width,width), "pix":ppg, "density":4, "tree-thick":1.8})
  buffer = io.BytesIO()
  image.save(buffer, format="PNG")
  base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
  f = open("../../../img.uvtt", "w")
  map_json = {"software": "Pantheont",
    "creator": "Mark Norrish",
    "format": "0.3",
    "resolution": {
    "map_origin": {
      "x": 0,
      "y": 0
    },
    "map_size": {
      "x": width,
      "y": width
    },
      "pixels_per_grid": ppg
    },
      "line_of_sight": los,
      "portals":[],
      "environment": {
      "baked_lighting": False
    },
    "lights":
      [],
    "image": base64_image
  }
  f.write(simplejson.dumps(map_json, indent=2))
  f.close()
