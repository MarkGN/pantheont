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

if __name__ == "__main__":
  pass
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