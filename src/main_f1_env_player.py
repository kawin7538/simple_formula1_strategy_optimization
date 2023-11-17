from datetime import timedelta
from f1_env.f1_env import F1Env
from utils.visualization import F1SimVisualization

env=F1Env()

observation, info = env.reset()

answer_reward=0
for i in range(66*28):
    action=env.action_space.sample()
    observation, reward, terminated, _, _ = env.step(action)

    if not terminated:
        answer_reward+=reward
    else:
        print("Car DNF at lap",i//28)
        print("Time Elapsed before DNF",timedelta(seconds=-answer_reward))
        answer_reward=reward
        break;
print("sum answer_reward",answer_reward)