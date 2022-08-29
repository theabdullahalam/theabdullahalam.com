import random
import time

thelist = [x for x in range(0, 1000)]

def random_with_choice(iters):
  for i in range(0, iters):
    random_list = random.choice(thelist, )