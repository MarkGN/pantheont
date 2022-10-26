import character, random

def roll():
  return 2+random.randint(1,6)

def random_mission(params={}):
  threat = params.get("threat", {})
  # threat should be a dict with params leader, minions, threat_ix, minion_type
  if not threat:
    threat_case = random.randint(1,1)
    if threat_case == 1:
      leader = character.boss()
      minions = [character.standard_man() for _ in range(roll())]
      gang_type = random.choice("slave rebellion; aggressive gang of smugglers; spate of criminal activity".split("; "))
      initial_location = random.choice("farm; mine; nexus".split("; "))
      print(f"There's been a {gang_type} at a nearby {initial_location}. A leader named {leader.name} has {len(minions)} henchmen.")
      print(leader)

if __name__ == "__main__":
  random_mission()