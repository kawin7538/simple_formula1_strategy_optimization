from f1_env.f1_env import F1Env

env=F1Env()

print(env.action_space)
print(env.action_space.shape)
print(env.action_space.is_np_flattenable)

print(env.action_space.sample())
print(env.action_space.sample())
print(env.action_space.sample())
print(env.action_space.sample())
print(env.action_space.sample())