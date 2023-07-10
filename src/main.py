import random

default_focus = 9
die_sides = 20
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
    ns = set([n for (n,_) in ns_ps])
    ns_ps_summed = [(n, sum([p for (n0,p) in ns_ps if n==n0])/damage_die_sides) for n in ns]
    hits[i] = (ns_ps_summed, sum([n*p for (n,p) in ns_ps_summed]))
  return hits

def expected_overkill(pow_adv, focus=default_focus):
  overkill = [0 for i in range(focus+1)]
  for i in range(1, focus+1):
    overkill[i] = sum([overkill[i-d] if i-d >= 0 else d-i for d in dmg_range(pow_adv)])/damage_die_sides
  return overkill

# Probability distribution over possible overkills
# Entry number h is the list of overkills and probabilities from h focus
def p_overkill(pow_adv, focus=default_focus):
  overkill = [[(0,1)] for i in range(focus+1)]
  for i in range(1, focus+1):
    vs = [o for d in dmg_range(pow_adv) for o in (overkill[i-d] if i>=d else [(d-i,1)])]
    ns = set([n for (n,_) in vs])
    overkill[i] = [(n, sum([p for (n0,p) in vs if n==n0])/damage_die_sides) for n in ns]
  return overkill

# Probability that character A beats B with the given advantages, which may be negative.
def p_win(combat_adv, pow_adv, end_adv, focus=default_focus, my_boons={}, his_boons={}, die=die_sides):
  # M[i][j] = p (I win given I have i focus left and he has j)
  my_focus = focus + ("stubborn" in my_boons)
  his_focus = focus + ("stubborn" in his_boons)
  overwhelm = lambda dmg, f, fmax : dmg * 4 >= 3*fmax
  # overwhelm = lambda dmg, f, fmax: dmg * 4 >= 3*f
  p_win_clash = min(1, max(0, (die//2+combat_adv)/die))
  odds_matrix = [[0 for i in range(his_focus+1)]] + [([1]+[None for i in range(his_focus)]) for j in range(my_focus)]
  for i in range(1,my_focus+1):
    for j in range(1,his_focus+1):
      if "overwhelm" in my_boons:
        odds_matrix[i][j] = p_win_clash * sum([odds_matrix[i][max(0,0 if overwhelm(dmg,j,his_focus) else j-dmg)] for dmg in dmg_range(pow_adv)])/damage_die_sides + (1-p_win_clash) * sum([odds_matrix[max(0,i-dmg)][j] for dmg in dmg_range(-end_adv)])/damage_die_sides
      else:
        odds_matrix[i][j] = p_win_clash * sum([odds_matrix[i][max(0,j-dmg)] for dmg in dmg_range(pow_adv)])/damage_die_sides + (1-p_win_clash) * sum([odds_matrix[max(0,i-dmg)][j] for dmg in dmg_range(-end_adv)])/damage_die_sides
  return odds_matrix[my_focus][his_focus]

# TODO Is there some elegant way to combine this and the above in one function?
# Obviously "if trapper in his_boons, do this code, else that", but there's no difference.
# The code is almost the same, but not quite, and there are plenty of almost-but-not
# effects with the same deal.
# TODO Trapper duels. A bit harder, since hits don't always advance the game state.
# If I start with him trapped, then p-win = p-win-now/(p-win-now + p-lose-now*p-he-then-wins).
def p_win_v_trapper(combat_adv, pow_adv, end_adv, focus=default_focus, die=die_sides):
  my_focus, his_focus = focus, focus
  p_win_clash = min(1, max(0, (die//2+combat_adv)/die))
  trap_disadvantage = 4
  p_win_clash_trapped = min(1, max(0, (die//2+(combat_adv-trap_disadvantage))/die))
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

def test_survival_time(pow_adv=0):
  print("=== Survival time vs POW advantage {pow} ===".format(pow=pow_adv))
  print("For each amount of hp, probabilities of going down in how many hits, and expected number")
  p = p_hits_to_incap(pow_adv)
  for ix,(l,exp) in enumerate (p):
    print(ix, l, exp)

def test_survival_odds():
  print("=== Win chances ===")
  print("Baseline: should be 0.5")
  print(p_win(0,0,0))
  print("With +combat")
  for i in range(1,6):
    print(i, p_win(i,0,0))
  print("With +POW")
  for i in range(1,6):
    print(i, p_win(0,i,0))
  print("With +POW and overwhelm")
  for i in range(1,6):
    print(i, p_win(0,i,0, my_boons=["overwhelm"]))
  print("With +END")
  for i in range(1,6):
    print(i, p_win(0,0,i))
  print("With +combat vs +END")
  for i in range(1,6):
    print(i, p_win(i,-i,0))
  print("With +combat vs +POW")
  for i in range(1,6):
    print(i, p_win(i,0,-i))
  print("With +POW and overwhelm vs +combat")
  for i in range(0,6):
    print(i, p_win(-i,i,0,my_boons = ["overwhelm"]))
  print("With stubborn")
  print(p_win(0,0,0,my_boons = ["stubborn"]))
  print("vs a trapper")
  print(p_win_v_trapper(0,0,0))
  print("With +combat")
  for i in range(1,6):
    print(i, p_win_v_trapper(i,0,0))
  print("With +POW")
  for i in range(1,6):
    print(i, p_win_v_trapper(0,i,0))
  print("With +END")
  for i in range(1,6):
    print(i, p_win_v_trapper(0,0,i))
  print("With +combat vs +END")
  for i in range(1,6):
    print(i, p_win_v_trapper(i,-i,0))
  print("With +combat vs +POW")
  for i in range(1,6):
    print(i, p_win_v_trapper(i,0,-i))
  
if __name__ == "__main__":
  print("Params: HP {hp}, damage offset {dmg}, cards {cards}, damage die {dmg_die}".format(hp=default_focus, dmg=damage_offset, cards=die_sides, dmg_die=damage_die_sides))
  
  for i in range(-4,5):
    test_survival_time(i)
  # test_survival_odds()

  # print("=== Expected overkill ===")
  # for i in range(-4,5):
  #   print(i, expected_overkill(i))
  # print(i, p_overkill(i))