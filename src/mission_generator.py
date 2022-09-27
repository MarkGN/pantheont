import character, random

def random_mission(params={}):
  threat = params.get("threat", {})
  # threat should be a dict with params leader, minions, threat_ix, minion_type
  if not threat:
    threat_case = random.randint(1,6)
    if threat_case == 1:
      threat["leader"] = character.boss()

if __name__ == "__main__":
  NotImplementedError