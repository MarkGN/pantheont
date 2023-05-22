import character, random

def roll():
  return 2+random.randint(1,6)

# TODO the problem here is that there's a whole world of subtle conditionality here.
# If it's coastal, there probably won't be many Drunts.
# So coasts and Drunts need some sort of tag to indicate that they probably won't co-occur.
# A DW is probably only applicable in case of a shipwreck or lost caravan.
# So, each threat needs a list of which locations it's game for;
# each task needs to be keyed to the threat;
# and each threat is itself highly complex.
# What I want is to factor these things out. There's the threat string, assets, other details, location, job.
def random_mission(params={}):
  threat = params.get("threat", {})
  # threat should be a dict with params leader, minions, threat_ix, minion_type
  if not threat:
    threat_case = random.randint(1,2)
    if threat_case == 1:
      human = True
      leader = character.boss()
      minions = [character.standard_man() for _ in range(roll())]
      gang_ix = random.randint(0,2)
      gang_type = ("slave rebellion; aggressive gang of smugglers; spate of criminal activity".split("; "))[gang_ix]
      initial_location = random.choice("farm; tunnel; nexus".split("; "))
      final_location = initial_location if random.random() < 0.5 else random.choice("bridge; forest; fortress".split("; "))
      apostrophe="'"
      threat = (f"There{apostrophe+'s' if initial_location==final_location else ' was'} {'an' if gang_ix==1 else 'been a'} {gang_type} at a nearby {initial_location}{'' if initial_location==final_location else ', but they'+apostrophe+'ve since moved to a ' + final_location}. A leader named {leader.name} has {len(minions)} henchmen.")
    elif threat_case == 2:
      human = True
      leader = character.boss()
      minions = [character.standard_man() for _ in range(roll())]
      cult = random.choice("Drunt; Hamant; Hezukelt; Irunt; Silloant".split("; "))
      backstory = random.choice("gained power in the local village; been driven out of their own village; been sent as missionaries".split("; "))
      location = random.choice("fortress; tunnel; nexus".split("; "))
      crime = {"Drunt":"commit arson", "Hamant":"cultivate paikera", "Hezukelt":"worship the kaiju", "Irunt":"attack travellers", "Silloant": "raid remote farms"}[cult]
      threat = (f"Having recently {backstory}, {cult}s have moved into a nearby abandoned {location}. They're finished settling in, and have started to {crime}.{' They will have lots of magic support.' if location=='nexus' else ''} A leader named {leader.name} has {len(minions)} henchmen.")
  print(threat)

def random_mission_2():
  den_locations = "abandoned mansion, abandoned sawmill, clearing, woodsman's hut, Nexus, old fortress, old temple, tunnel".split(", ")
  lurk_locations = "bridge, crossroad, Nexus, tunnel".split(", ")
  opposition = {
    "minion_type": "human",
    "minion_number": random.randint(3,8),
    "leader": character.boss(),
    "den": random.choice(den_locations),
    "lurk": random.choice(lurk_locations),
    "activity": "stealing stuff",
    "backstory": "because they're douches"
  }
  threat_ix = random.randint(1,6)
  roll = random.randint(1,1)
  if roll == 1:
    roll_2 = random.randint(0,2)
    opposition["minion_type"] = "smuggler, rebel slave, robber".split(", ")[roll_2]
    opposition["activity"] = "moving contraband and attacking anyone who gets near; attacking Garents and their retainers; stealing anything they can get their hands on".split("; ")[roll_2]
    opposition["backstory"] = "because the local Silloant matron decided to expand; after years of abuse; because they're douches".split("; ")[roll_2]
  elif roll == 2:
    roll_2 = random.randint(0,5)
    opposition["minion_type"] = "Drunt, Hamant men, Hamant women, Hezukelt, Silloant".split(", ")[roll_2]
    opposition["activity"] = ""

  location_story = f"They're camped out in a{'n' if opposition['den'][0] in 'aeiou' else ''} {opposition['den']} and are attacking anyone who gets too close" if opposition["den"] == opposition["lurk"] else f"They're camped out in a{'n' if opposition['den'][0] in 'aeiou' else ''} {opposition['den']}, but are attacking people near a {opposition['lurk']}"
  story = f"{opposition['leader'].name} and his {opposition['minion_number']} {opposition['minion_type']}s are {opposition['activity']}. {location_story}. They began {opposition['backstory']}."
  print(story)
  return opposition

if __name__ == "__main__":
  random_mission_2()