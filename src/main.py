import random

class Character:
  def __init__(self, pow=10, end=10, boons=[]) -> None:
    pass

def expected_hits_to_incap(focus, pow_adv):
  hits = [0 for _ in range(focus+1)]
  dmg_range = [2+max(0,roll+pow_adv) for roll in range(1,7)]
  for i in range(1,focus+1):
    hits[i] = sum([hits[max(0, i-d)] for d in dmg_range])/6 + 1
  return hits

def expected_overkill(pow_adv, focus):
  dmg_range = [2+max(0,roll+pow_adv) for roll in range(1,7)]
  overkill = [0 for i in range(focus+1)]
  for i in range(1, focus+1):
    overkill[i] = sum([overkill[i-d] if i-d >= 0 else d-i for d in dmg_range])/6
  return overkill

# Probability that character A beats B with the given advantages, which may be negative. Both have equal focus and no boons.
# TODO give an options param, one being for Overwhelming: I'd like to see what that does for high-POW builds.
# WTH is the algorithm for that? If 'overwhelming' in params, M[i][j] = ... M[i][max(0, 0 if dmg >= 0.75*j else j-dmg)] ...
def p_win(combat_adv, pow_adv, end_adv, focus=14, my_boons={}, his_boons={}):
  # M[i][j] = p (I win given I have i focus left and he has j)
  my_focus = focus + ("stubborn" in my_boons)
  his_focus = 8 if "minion" in his_boons else focus + ("stubborn" in his_boons)
  p_win_clash = min(1, max(0, (13+combat_adv)/26))
  odds_matrix = [[0 for i in range(his_focus+1)]] + [([1]+[None for i in range(his_focus)]) for j in range(my_focus)]
  for i in range(1,my_focus+1):
    for j in range(1,his_focus+1):
      if "overwhelm" in my_boons:
        odds_matrix[i][j] = p_win_clash * sum([odds_matrix[i][max(0,0 if 3*dmg >= 2*his_focus else j-dmg)] for dmg in [2+max(0,r+pow_adv) for r in range(1,7)]])/6 + (1-p_win_clash) * sum([odds_matrix[max(0,i-dmg)][j] for dmg in [2+max(0,r-end_adv) for r in range(1,7)]])/6
      else:
        odds_matrix[i][j] = p_win_clash * sum([odds_matrix[i][max(0,j-dmg)] for dmg in [2+max(0,r+pow_adv) for r in range(1,7)]])/6 + (1-p_win_clash) * sum([odds_matrix[max(0,i-dmg)][j] for dmg in [2+max(0,r-end_adv) for r in range(1,7)]])/6
  return odds_matrix[my_focus][his_focus]

# run a bunch of sims and approximate it; useful for boons doing weird stuff like anbinden
def p_win_monte_carlo(its, combat_adv, pow_adv, end_adv, focus=14, my_boons={}, his_boons={}):
  return NotImplementedError

# iterable :: [([String], Int)]
# an entry like (["a", "b", "cd"], 2) means it will sample 2 of the list and concatenate them
# (l, 0) means either 0 or 1 copies
def name_from_lists(iterable):
  return "".join(["".join(random.sample(alphabet, random.randint(0,1) if num==0 else num)) for (alphabet, num) in iterable])

def random_name_flower(params={}):
  prefixes = "black,blue,lady's,scarlet,sea,white,yellow".split(",")
  suffixes = "berry,cap,cress,fern,glove,root,weed,wood,wort".split(",")
  return " ".join((random.choice(prefixes), random.choice(suffixes)))

# Make a random name based on katakana
def random_name_kana(params={}):
  consonants = list("bdghjkmnprstwz") + "ch,sh,ts".split(",")
  vowels = list("aeiou") + ["ai"]
  masculine_vowels = list("eiou")
  feminine_vowels = ["a", "ai"]
  sex = params.get("sex", "male")
  seed = params.get("seed", random.random())
  if sex == "male":
    if seed < 0.5:
      return name_from_lists([(consonants, 0), (["y"], 0), (vowels, 1), (["n"], 0), (consonants, 1), (masculine_vowels, 1), (["n"], 0)])
    else:
      return name_from_lists([(consonants, 0), (vowels, 1), (consonants, 1), (vowels, 1), (consonants, 1), (masculine_vowels, 1), (["n"], 0)])
  else:
    if seed < 0.5:
      return name_from_lists([(consonants, 0), (["y"], 0), (vowels, 1), (["n"], 0), (consonants, 1), (feminine_vowels, 1), (["n"], 0)])
    else:
      return name_from_lists([(consonants, 0), (vowels, 1), (consonants, 1), (vowels, 1), (consonants, 1), (feminine_vowels, 1), (["n"], 0)])

# TODO Some of these longer names are a bit of a mouthful. A real one like Antoinette or Christina, phonics aside, would be "Antwonet" or "Kristina", only 3 vowels and 5 consonants total. These memoryless models giving things like "Aisjesria" are really a budget of 4 syllables.
# What if I make a budget-based model? One to three vowels, diphthongs count as two, similar for consonants?
# Probably overkill. I mean, I want patterns of the form consonant cluster - vowel cluster - consonant cluster - ..., right?
# Subject to rules like "no more than three vowel clusters", "terminal feminine/masculine vowel", "no more than four total vowels", "no more than five total consonants".
# TODO these names are ridiculous. Figure it out.
# There should be separate initial clusters, mid, and terminal, because bl works at start mid but not end, lm works mid end but not start, etc.
def random_name(params={}):
  vowels = list("aeiou") + ["ai", "ao", "au", "ia", "ie", "oi"]
  masculine_terminal_vowels = list("eiou") + ["ai", "ao", "au", "ie", "oi"]
  consonants = "bcdfghjklmnpqrstvwxyz"
  digraphs = ["ch", "fj", "sh", "sk", "th", "ts", "zh"]
  initial_digraphs = ["ch", "dz", "gj", "fj", "kj", "sh", "sk", "st", "th", "zh"]
  terminal_digraphs = ["ch", "sh", "sk", "th"]
  initial_consonants = list("bdfghjklmnprstvwz") + initial_digraphs
  pre_consonant_consonants = list("bdfgkps")
  post_consonant_consonants = list("jlrw")
  terminal_consonants = list("dfklmnrstz") + terminal_digraphs
  middle_consonant_clusters = list("bdfghjklmnprstvwz") + initial_digraphs + [c1+c2 for c1 in pre_consonant_consonants+list("lst") for c2 in post_consonant_consonants+list("nst") if c1 != c2]
  feminine_terminal_consonants = "klnrstz"
  feminine_suffix_vowels = ["a" for _ in range(3)] + ["ia"]
  sex = params.get("sex", "male")
  seed = random.random()
  if sex == "male":
    if seed < 0.3:
      return name_from_lists([(pre_consonant_consonants, 0), (post_consonant_consonants, 1), (masculine_terminal_vowels, 1), (terminal_consonants, 1)])
    if seed < 0.55:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (pre_consonant_consonants, 0), (post_consonant_consonants, 1), (masculine_terminal_vowels, 1), (terminal_consonants, 1)])
    if seed < 0.8:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (pre_consonant_consonants, 1), (post_consonant_consonants, 0), (masculine_terminal_vowels, 1), (terminal_consonants, 1)])
    if seed < 1:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), ("-", 1), (pre_consonant_consonants, 0), (post_consonant_consonants, 0), (masculine_terminal_vowels, 1), (terminal_consonants, 1)])
  else:
    if seed < 0.1:
      return name_from_lists([(pre_consonant_consonants, 0), (post_consonant_consonants, 1), (feminine_suffix_vowels, 1), (feminine_terminal_consonants, 0)])
    if seed < 0.3:
      return name_from_lists([(initial_consonants, 1), (feminine_suffix_vowels, 1), (feminine_terminal_consonants, 0)])
    if seed < 0.4:
      return name_from_lists([(initial_consonants, 1), (vowels, 1), (" ", 1), (pre_consonant_consonants, 0), (post_consonant_consonants, 1), (feminine_suffix_vowels, 1), (feminine_terminal_consonants, 0)])
    if seed < 0.7:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (middle_consonant_clusters, 1), (feminine_suffix_vowels, 1), (feminine_terminal_consonants, 0)])
    if seed < 0.9:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (middle_consonant_clusters, 1), (vowels, 1), (" ", 1), (pre_consonant_consonants, 0), (post_consonant_consonants, 1), (feminine_suffix_vowels, 1), (feminine_terminal_consonants, 0)])
    if seed < 1:
      return name_from_lists([(vowels, 1), (middle_consonant_clusters, 1), (vowels, 1), (middle_consonant_clusters, 1), (feminine_suffix_vowels, 1), (feminine_terminal_consonants, 0)])

if __name__ == "__main__":
  # print(expected_hits_to_incap(16,1))
  # print(expected_hits_to_incap(16,0))
  # print(expected_hits_to_incap(16,-1))
  # print(expected_hits_to_incap(150,0)[130:])

  # print(p_win(1,0,0))
  # print(p_win(0,1,0))
  # print(p_win(0,0,1))
  # print(p_win(3,0,0))
  # print(p_win(0,3,0))
  # print(p_win(0,0,3))
  # print(p_win(5,0,0))
  # print(p_win(0,5,0))
  # print(p_win(0,0,5))

  # print(p_win(0,0,0, my_boons = ["overwhelm", "stubborn"]))
  # print(p_win(0,0,0, my_boons = ["overwhelm"]))
  # print(p_win(0,0,0, my_boons = ["stubborn"]))

  # print(p_win(0,0,0, my_boons = ["overwhelm"], his_boons=["minion"]))
  # print(p_win(0,0,0, my_boons = [], his_boons=["minion"]))
  # print(p_win(0,1,0, my_boons = ["overwhelm"], his_boons=["minion"]))
  # print(p_win(0,1,0, my_boons = [], his_boons=["minion"]))
  # print(p_win(0,1,0, his_boons = ["stubborn"]))

  # print(p_win(-1,0,0))
  # print(p_win(0,-1,0))
  # print(p_win(0,0,-1))
  # print(p_win(1,-1,0))
  # print(p_win(1,0,-1))
  # print(p_win(0,1,-1))
  # print(p_win(5,-5,0))
  # print(p_win(5,0,-5))
  # print(p_win(0,5,-5))

  # print(expected_overkill(0,16))
  # print(expected_overkill(1,16))
  # print(expected_overkill(2,16))
  # print(expected_overkill(-1,16))
  # print(expected_overkill(-2,16))

  # for (t,herb) in [("active", "fruit"), ("amper", "leaf"), ("damper", "root"), ("preservative", "resin")]:
  #   for _ in range(3):
  #     colors = random.sample({"red", "orange", "yellow", "green", "blue", "purple"}, 2)
  #     print(random_name_flower(), herb+":", t+";", colors[0], colors[1])

  for i in range(10):
    print(random_name())
    print(random_name({"sex":"female"}))
    print(random_name_kana())
    print(random_name_kana({"sex": "female"}))
    print(random_name_flower())

