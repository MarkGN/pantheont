
class Stats:
  def __init__(self,*args):
    stats = "agi,pow,end,met,mas,ath,fig,kno,mag,ste,vig".split(",")
    num_stats = len(stats)
    assert(len(args)==num_stats)
    for ix in range(len(num_stats)):
      setattr(self,stats[ix],args[ix])

class Character:
  # Is this lazy or bad practice? Who knows.
  # It's not really ideal here, because there are 11 stats that everyone has, and writing down the keys is a bit gross
  # TODO make the first 11 be stats, then I guess boons, gear, spells, then any other params
  def __init__(self, params):
    for key, value in params:
      if key == "stat":
        self.agi, =value[0]
      else:
        setattr(self, key, value)

def everyman():
  return Character({"agi":10,"pow":10,"end":10,"met":10,"mas":10})

def boss():
  return NotImplementedError