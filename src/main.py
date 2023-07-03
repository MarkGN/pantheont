import random

default_focus = 9
die_sides = 28
damage_die_sides = 6
damage_offset = 0

class Character:
  def __init__(self, pow=5, end=5, boons=[]) -> None:
    pass

def dmg_range(pow_adv):
  return [max(1, pow_adv+damage_offset+i) for i in range(1, damage_die_sides+1)]

def expected_hits_to_incap(pow_adv=0, focus=default_focus):
  hits = [0 for _ in range(focus+1)]
  for i in range(1,focus+1):
    hits[i] = sum([hits[max(0, i-d)] for d in dmg_range(pow_adv)])/damage_die_sides + 1
  return hits

def p_hits_to_incap(pow_adv=0, focus=default_focus):
  hits = [None for _ in range(focus+1)]
  hits[0] = [(0,1)],0 # n_hits:p_n
  for i in range(1,focus+1):
    ns_ps = [(n+1, p) for dmg in dmg_range(pow_adv) for (n,p) in hits[max(0,i-dmg)][0]]
    ns = list(set([n for (n,_) in ns_ps]))
    ns_ps_summed = [(n, sum([p for (n0,p) in ns_ps if n==n0])/damage_die_sides) for n in ns]
    hits[i] = (ns_ps_summed, sum([n*p for (n,p) in ns_ps_summed]))
  return hits

def expected_overkill(pow_adv, focus=default_focus):
  overkill = [0 for i in range(focus+1)]
  for i in range(1, focus+1):
    overkill[i] = sum([overkill[i-d] if i-d >= 0 else d-i for d in dmg_range(pow_adv)])/damage_die_sides
  return overkill

# Probability that character A beats B with the given advantages, which may be negative. Both have equal focus and no boons.
# TODO let boons include Net, 
def p_win(combat_adv, pow_adv, end_adv, focus=default_focus, my_boons={}, his_boons={}, die=die_sides):
  # M[i][j] = p (I win given I have i focus left and he has j)
  my_focus = focus + ("stubborn" in my_boons)
  his_focus = 8 if "minion" in his_boons else focus + ("stubborn" in his_boons)
  p_win_clash = min(1, max(0, (die//2+combat_adv)/die))
  odds_matrix = [[0 for i in range(his_focus+1)]] + [([1]+[None for i in range(his_focus)]) for j in range(my_focus)]
  for i in range(1,my_focus+1):
    for j in range(1,his_focus+1):
      if "overwhelm" in my_boons:
        odds_matrix[i][j] = p_win_clash * sum([odds_matrix[i][max(0,0 if 3*dmg >= 2*his_focus else j-dmg)] for dmg in dmg_range(pow_adv)])/damage_die_sides + (1-p_win_clash) * sum([odds_matrix[max(0,i-dmg)][j] for dmg in dmg_range(-end_adv)])/damage_die_sides
      else:
        odds_matrix[i][j] = p_win_clash * sum([odds_matrix[i][max(0,j-dmg)] for dmg in dmg_range(pow_adv)])/damage_die_sides + (1-p_win_clash) * sum([odds_matrix[max(0,i-dmg)][j] for dmg in dmg_range(-end_adv)])/damage_die_sides
  return odds_matrix[my_focus][his_focus]

def p_win_v_trapper(combat_adv, pow_adv, end_adv, focus=default_focus, die=die_sides):
  my_focus, his_focus = focus, focus
  p_win_clash = min(1, max(0, (die//2+combat_adv)/die))
  p_win_clash_trapped = min(1, max(0, (die//2+(combat_adv-5))/die))
  odds_matrix = [[[0 for i in range(his_focus+1)]] + [([1]+[None for i in range(his_focus)]) for j in range(my_focus)] for trapped in range(2)]
  for i in range(1,my_focus+1):
    for j in range(1,his_focus+1):
      odds_matrix[1][i][j] = p_win_clash_trapped * sum([odds_matrix[0][i][max(0,j-dmg)] for dmg in dmg_range(pow_adv)])/damage_die_sides + (1-p_win_clash_trapped) * sum([odds_matrix[1][max(0,i-dmg)][j] for dmg in dmg_range(-end_adv)])/damage_die_sides
      odds_matrix[0][i][j] = p_win_clash * sum([odds_matrix[0][i][max(0,j-dmg)] for dmg in dmg_range(pow_adv)])/damage_die_sides + (1-p_win_clash) * odds_matrix[1][i][j]
  return odds_matrix[0][my_focus][his_focus]

# run a bunch of sims and approximate it; useful for boons doing weird stuff like anbinden
def p_win_monte_carlo(its, combat_adv, pow_adv, end_adv, focus=14, my_boons={}, his_boons={}, die=14):
  wins = 0
  for i in range(its):
    my_focus = focus + ("stubborn" in my_boons)
    his_focus = 8 if "minion" in his_boons else focus + ("stubborn" in his_boons)
    my_tokens = dict()
    his_tokens = dict()
    while my_focus > 0 and his_focus > 0:
      if random.randint(1-die, die) + combat_adv + his_tokens.get("fatigue", 0) - my_tokens.get("fatigue", 0) > 0:
        if "hypno" in my_boons:
          his_tokens["fatigue"] = his_tokens.get("fatigue", 0)
          his_tokens["fatigue"] += 2+max(0, pow_adv + random.randint(1,6))
          if his_tokens["fatigue"] >= 10:
            his_focus = 0
        else:
          his_focus -= 2+max(0, pow_adv + random.randint(1,6))
      else:
        my_focus -= 2+max(0, -end_adv + random.randint(1,6))
      # print(my_focus, his_focus, his_tokens.get("fatigue", 0), my_tokens.get("fatigue", 0))
    if my_focus > 0:
      wins += 1
  return wins/its

if __name__ == "__main__":
  pass
  p = p_hits_to_incap()
  for l in p:
    print(l)
  # es = [expected_hits_to_incap(i)[-1] for i in range(-5,6)]
  # print(es)
  # for i in range(len(es)-1):
  #   print(es[i]/es[i+1])
  # print(expected_hits_to_incap(150,0)[130:])

  # print("Expected hits to incapacitate")
  # print([(i,expected_hits_to_incap(0, i)[-1]) for i in range(default_focus+1)])

  # print("Win chances for AGI POW END")

  # print(p_win_v_trapper(0,0,0))
  # print("AGI")
  # print(p_win(1,0,0))
  # print(p_win(3,0,0))
  # print(p_win(5,0,0))
  # print("vs trapper")
  # print(p_win_v_trapper(1,0,0))
  # print(p_win_v_trapper(3,0,0))
  # print(p_win_v_trapper(5,0,0))
  # print("POW")
  # print(p_win(0,1,0))
  # print(p_win(0,3,0))
  # print(p_win(0,5,0))
  # print("vs trapper")
  # print(p_win_v_trapper(0,1,0))
  # print(p_win_v_trapper(0,3,0))
  # print(p_win_v_trapper(0,5,0))
  # print("POW w overwhelming")
  # print(p_win(0,1,0,my_boons = ["overwhelm"]))
  # print(p_win(0,3,0,my_boons = ["overwhelm"]))
  # print(p_win(0,5,0,my_boons = ["overwhelm"]))
  # print("END")
  # print(p_win(0,0,1))
  # print(p_win(0,0,3))
  # print(p_win(0,0,5))
  # print("vs trapper")
  # print(p_win_v_trapper(0,0,1))
  # print(p_win_v_trapper(0,0,3))
  # print(p_win_v_trapper(0,0,5))

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
  # print(p_win(-5,5,0))
  # print(p_win(5,0,-5))
  # print(p_win(0,5,-5))
  # print("AGI vs POW, vs END")
  # print(p_win(1,0,-1))
  # print(p_win(1,-1,0))
  # print("+POW, -AGI")
  # for i in range(1,6):
  #   print(p_win(-i,i,0))
  #   print(p_win(-i,i,0,my_boons = ["overwhelm"]))

  # for i in range(-4,5):
  #   print(i, expected_overkill(i))

  # for (t,herb) in [("active", "fruit"), ("amper", "leaf"), ("damper", "root"), ("preservative", "resin")]:
  #   for _ in range(3):
  #     colors = random.sample({"red", "orange", "yellow", "green", "blue", "purple"}, 2)
  #     print(random_name_flower(), herb+":", t+";", colors[0], colors[1])

  # d=20
  # def cardy(i):
  #   return (13+i)/(13-i)
  # def oppo(i):
  #   return (d*(d+1) + 2*d*(i-1))/((d-i)*(d-i-1))
  # for i in range(12):
  #   print(i)
  #   print(cardy(i), cardy(i+1)/cardy(i))
  #   print(oppo(i), oppo(i+1)/oppo(i))

  # for i in range(10):
  #   print(i, p_win_monte_carlo(10000, -i, 0, 0, focus=default_focus, my_boons={"hypno"}))