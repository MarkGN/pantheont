import base64
import io
from PIL import Image, ImageDraw
from shapely.geometry import Point, Polygon
import math, random, simplejson, scipy
from scipy.spatial import Delaunay
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

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

# This should be like build-river, but more sophisticated.
# Begin with a line; recursively, replace each segment with one bending left or right
# by some amount
def build_path(start, end, params={}):
  num_kinks=2
  min_kink=0.3
  max_kink=0.5
  wo2=params.get("width",200)/2
  path = [start, end]
  for _ in range(num_kinks):
    segments = [(path[i],path[i+1]) for i in range(len(path)-1)]
    drns = [math.atan2((y2-y1),(x2-x1)) for ((x1,y1),(x2,y2)) in segments]
    dists = [math.dist(s,e) for (s,e) in segments]
    for i in range(len(segments)):
      x,y = segments[i][0]
      var = (1 if random.randint(0,1) else -1) * (min_kink + random.random()*(max_kink-min_kink))
      drn = drns[i] + var
      dist = dists[i] / math.cos(var) * (1+(random.random()-0.5)/10)
      x += round(0.5 * dist * math.cos(drn))
      y += round(0.5 * dist * math.sin(drn))
      segments[i] = (segments[i][0]), (x,y)
    path = [s for segment in segments for s in segment] + [end]
  # recompute drns;
  # for point in path, go point shifted perp to drn by wo2, then in other drn
  drns = [None for i in range(len(path))]
  for i in range(len(path)):
    (x1,y1) = path[max(0,i-1)]
    (x2,y2) = path[min(len(path)-1,i+1)]
    drns[i]=math.atan2(y2-y1,x2-x1)
  # return path
  poly = [None for i in range(2*len(path)+1)]
  for i in range(len(path)):
    x,y=path[i]
    poly[i] = x+wo2*-math.sin(drns[i]), y+wo2*math.cos(drns[i])
    poly[2*len(path)-1-i] = x+wo2*math.sin(drns[i]), y+wo2*-math.cos(drns[i])
    # poly[i] = path[i]
    # poly[2*len(path)-1-i] = path[i]
  poly[-1]=poly[0]
  return poly

# TODO factor stuff out, like creating trees
# TODO So this is pretty cool, but it'd be nice to be able to say:
# 1) I want grass, trees;
# 2) I want a clearing, maybe even with some traveller bedrolls;
# 3) I want a stream, which might even branch
# ... and it'd be nice to wrap it in a separate function creating multiple terrains,
# so that eg I could have a cave system
def build_forest(params={}):
  sx,sy = size = params.get("size", (500,500))
  density = params.get("density", 1)
  tree_thickness = params.get("tree-thick", 1.8)
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

def build_cave(params):
  # TODO much of this is shared boilerplate from build-forest and should be factored out
  # TODO add a pathway from a room to outside. 
  sx,sy = size = params.get("size", (5000,5000))
  floor_color = (155,155,155)
  brown = (130, 130, 0)
  out = Image.new("RGB", size, brown)
  d = ImageDraw.Draw(out)
  border = 50
  d.rectangle([(border, border), (sx-border,sy-border)], fill=floor_color)
  line_of_sight = []
  room_rad_min = params.get("rrm",100)
  room_rad_max = params.get("rrm",300)
  sepsq = params.get("sep-sq", 500**2)
  ppg = params.get("pix",1) # pixels per grid unit
  
  # So here's the plan: I generate my polygonal rooms and corridors; join with union;
  # then draw outlines and VBL about the exterior and interiors.
  # Suggestion: Delaunay triangulation, using the centres of each room.
  # I do that, generate a minimum spanning tree, randomly delete some fraction of the
  # other edges, then generate corridors along the other edges.
  # For corridors, calculate the displacement vectors; perturb a few points; and at each
  # point, shift left or right rand +/- width/2, 90 degrees.

  room_centres = []
  while len(room_centres) < (params.get("n-rooms", 5)):
    rx,ry = (random.randint(room_rad_max, sx - room_rad_max), random.randint(room_rad_max, sy - room_rad_max))
    if all([(rx-x)**2+(ry-y)**2 > sepsq for (x,y) in room_centres]):
      room_centres.append((rx,ry))
    
  rooms = []
  for (x,y) in room_centres:
    n_pts = 12
    room=[]
    for i in range(n_pts):
      theta = 2*math.pi*i/n_pts
      mult = room_rad_min + random.random()*(room_rad_max-room_rad_min)
      x1,y1 = x+mult*math.cos(theta), y+mult*math.sin(theta)
      room.append((x1,y1))
    room.append(room[0])
    rooms.append(room)

  # Add a 'room' that's outside, to force a path to it
  (x,y) = [(-sx,sy/2),(-sy,sx/2),(2*sx,sy/2),(2*sy,sx/2)][random.randint(0,3)]
  room_centres.append((x,y))
  # handle corridors
  # first, create delaunay triangulation
  simplices = Delaunay(room_centres).simplices
  simplices = [sorted(s) for s in simplices]
  paths = {(i,j) for simplex in simplices for i in simplex for j in simplex if i<j}
  # second, delete all long edges of obtuse triangles
  def distsq(a,b):
    (x1,y1)=room_centres[a]
    (x2,y2)=room_centres[b]
    return (x1-x2)**2+(y1-y2)**2
  def remove_long_edge(s):
    s.sort()
    d0=distsq(s[1],s[2])
    d1=distsq(s[0],s[2])
    d2=distsq(s[0],s[1])
    if d0>d1+d2:
      paths.discard((s[1],s[2]))
    if d1>d0+d2:
      paths.discard((s[0],s[2]))
    if d2>d0+d1:
      paths.discard((s[0],s[1]))
  for s in simplices:
    remove_long_edge(s)

  connection_graph = [[0 for _ in range(len(room_centres))] for _ in range(len(room_centres))]
  for (i,j) in paths:
    connection_graph[i][j]=distsq(i,j)
  mst = minimum_spanning_tree(connection_graph)
  xs,ys=mst.nonzero()
  indices = list(zip(xs,ys))
  paths = {p for p in paths if p in indices or random.random()<0.3}
  paths = {(room_centres[i],room_centres[j]) for (i,j) in paths}

  paths = [build_path(s,e) for (s,e) in paths]

  all_areas = Polygon([])
  for poly in rooms+paths:
    all_areas = all_areas.union(Polygon(poly))
  
  d.line(all_areas.exterior.coords,fill=(70,50,30),width=10)
  for p in all_areas.interiors:
    d.line(p.coords,fill=(50,40,30),width=10)
    line_of_sight.append([{"x":(x/ppg),"y":(y/ppg)} for (x,y) in p.coords])
  line_of_sight.append([{"x":(x/ppg),"y":(y/ppg)} for (x,y) in all_areas.exterior.coords])
  line_of_sight.append([{"x":0,"y":0},{"x":0,"y":sy/ppg},{"x":sx/ppg,"y":sy/ppg},{"x":sx/ppg,"y":0},{"x":0,"y":0}])

  return out, line_of_sight

if __name__=="__main__":
  ppg = 50
  width = 2500
  # image, los = build_forest(params={"size":(width,width), "pix":ppg, "density":4, "tree-thick":1.8})
  image, los = build_cave(params={"size":(width,width), "pix":ppg, "n-rooms":9})
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
