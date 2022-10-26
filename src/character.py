import random
import name_generator

stats = "agi,pow,end,met,mas,ath,fig,kno,mag,ste,vig".split(",")
attributes = "agi,pow,end,met,mas".split(",")
skills = "ath,fig,kno,mag,ste,vig".split(",")

def random_attribute_order():
  order = list(range(5))
  random.shuffle(order)
  return order

def biased_random_attribute_order(preferences):
  rolls = [preferences[i]*0.9+random.randint(1,6) for i in range(5)]
  return [len([j for j in range(5) if rolls[j]<rolls[i]]) for i in range(5)]

silloant_preferences = [1,3,4,2,5]

class Stats:
  def __init__(self,*args):
    num_stats = len(stats)
    assert(len(args)==num_stats)
    for ix in range(len(num_stats)):
      setattr(self,stats[ix],args[ix])

class Character:
  # Is this lazy or bad practice? Who knows.
  # It's not really ideal here, because there are 11 stats that everyone has, and writing down the keys is a bit gross
  # TODO make the first 11 be stats, then I guess boons, gear, spells, then any other params
  def __init__(self, params):
    for key, value in params.items():
      setattr(self, key, value)
    self.name = name_generator.random_name_kana()

  def __str__(self) -> str:
    return f"{self.name}: " + ", ".join([f"{attr}: {getattr(self, attr)}" for attr in stats]) + f". Boons: {self.boons}"

def everyman():
  return Character({"agi":5,"pow":5,"end":5,"met":5,"mas":5}|{skill:1 for skill in skills}|{"boons":{}})

# attr_order is some permutation of range(5)
def standard_man(attr_order = None):
  if not attr_order:
    attr_order = random_attribute_order()
  return Character({attributes[attr]:7-attr_order[attr] for attr in range(5)} | {skill:1 for skill in skills} | {"boons":{}})

def silloant():
  base = standard_man(biased_random_attribute_order(silloant_preferences))
  base.boons.add("gymnast")
  return base

# give +1 to every attr and skill; which is a massive advantage, +2 combat +1 POW +1 END, trading almost 2:1, and more if you consider he'll have either better gear or a combat style
def boss(base=standard_man(biased_random_attribute_order(silloant_preferences))):
  for stat in stats:
    setattr(base,stat,getattr(base,stat,0)+1)
  base.boons = {"marksman"}
  return base