import random

# iterable :: [([String], Int)]
# an entry like (["a", "b", "cd"], 2) means it will sample 2 of the list and concatenate them
# (l, 0) means either 0 or 1 copies
def name_from_lists(iterable):
  return "".join(["".join(random.sample(alphabet, random.randint(0,1) if num==0 else num)) for (alphabet, num) in iterable])

def random_name_flower(params={}):
  prefixes = "black,blue,lady's,scarlet,sea,white,yellow".split(",")
  suffixes = "berry,cap,cress,fern,glove,root,weed,wood,wort".split(",")
  return " ".join((random.choice(prefixes), random.choice(suffixes)))

def random_name_guttural(params={}):
  vowels = list("aeiou") + ["ai", "ao", "au", "ia", "ie", "oi"]
  masculine_terminal_vowels = list("eiou") + ["ai", "ao", "au", "ie", "oi"]
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

# Make a random name based on katakana
def random_name_kana(params={}):
  consonants = list("bdghjkmnprstwyz") + "ch,sh,ts".split(",")
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

# Make a random name based on latin phonics
def random_name_latin(params={}):
  vowels = list("aeiou") + ["ae", "au", "ia", "ie", "oi"]
  masculine_terminal_vowels = list("eiou") + ["ae", "au", "ie", "oi"]
  initial_digraphs = ["cl", "sc", "st"]
  terminal_digraphs = ["cl", "sc", "st"]
  initial_consonants = list("bcdfghjlmnprstwz") + initial_digraphs
  pre_consonant_consonants = list("bcdfgps")
  post_consonant_consonants = list("jlrw")
  terminal_consonants = list("cdflmnrstz") + terminal_digraphs
  terminal_masculine = [pre+suf for pre in terminal_consonants for suf in ["us", "ius", "o"]]
  middle_consonant_clusters = initial_consonants + ["cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "sc", "sl", "st", "tr"]
  # list("bcdfghjlmnprstvwz") + initial_digraphs + [c1+c2 for c1 in pre_consonant_consonants+list("lst") for c2 in post_consonant_consonants+list("nst") if c1 != c2]
  feminine_suffix_vowels = ["a" for _ in range(3)] + ["ia"]
  sex = params.get("sex", "male")
  seed = random.random()
  if sex == "male":
    if seed < 0.3:
      return name_from_lists([(pre_consonant_consonants, 0), (post_consonant_consonants, 1), (masculine_terminal_vowels, 1), (terminal_masculine, 1)])
    if seed < 0.55:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (pre_consonant_consonants, 0), (post_consonant_consonants, 1), (masculine_terminal_vowels, 1), (terminal_masculine, 1)])
    if seed < 0.8:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (pre_consonant_consonants, 1), (post_consonant_consonants, 0), (masculine_terminal_vowels, 1), (terminal_masculine, 1)])
    if seed < 1:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), ("-", 1), (pre_consonant_consonants, 0), (post_consonant_consonants, 0), (masculine_terminal_vowels, 1), (terminal_masculine, 1)])
  else:
    if seed < 0.1:
      return name_from_lists([(pre_consonant_consonants, 0), (post_consonant_consonants, 1), (feminine_suffix_vowels, 1)])
    if seed < 0.3:
      return name_from_lists([(initial_consonants, 1), (vowels, 1), (" ", 1), (pre_consonant_consonants, 0), (post_consonant_consonants, 1), (feminine_suffix_vowels, 1)])
    if seed < 0.5:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (middle_consonant_clusters, 1), (vowels, 1), (middle_consonant_clusters, 1), (feminine_suffix_vowels, 1)])
    if seed < 0.7:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (middle_consonant_clusters, 1), (feminine_suffix_vowels, 1)])
    if seed < 0.9:
      return name_from_lists([(initial_consonants, 0), (vowels, 1), (middle_consonant_clusters, 1), (vowels, 1), (" ", 1), (pre_consonant_consonants, 0), (post_consonant_consonants, 1), (feminine_suffix_vowels, 1)])
    if seed < 1:
      return name_from_lists([(vowels, 1), (middle_consonant_clusters, 1), (vowels, 1), (middle_consonant_clusters, 1), (feminine_suffix_vowels, 1)])

if __name__=="__main__":
  delim = ", "
  n = 10
  # print(" flowers")
  # print(" ".join([random_name_flower() for _ in range(n)]))
  print(" guttural boy")
  print(delim.join([random_name_guttural() for _ in range(n)]))
  print(" guttural girl")
  print(delim.join([random_name_guttural({"sex":"female"}) for _ in range(n)]))
  print(" kana boy")
  print(delim.join([random_name_kana({"sex":"male"}) for _ in range(n)]))
  print(" kana girl")
  print(delim.join([random_name_kana({"sex":"female"}) for _ in range(n)]))
  print(" latin boy")
  print(delim.join([random_name_latin({"sex":"male"}) for _ in range(n)]))
  print(" latin girl")
  print(delim.join([random_name_latin({"sex":"female"}) for _ in range(n)]))