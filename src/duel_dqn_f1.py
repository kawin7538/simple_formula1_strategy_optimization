import os
import argparse
from f1_env.xuance_f1_env import XuanceF1Env

from xuance.common import get_configs
from xuance.environment import REGISTRY_ENV

from xuance.environment import make_envs
from xuance.torch.agents import DuelDQN_Agent

REGISTRY_ENV['f1_env']=XuanceF1Env

if __name__ == '__main__':
    os.system('cls')

    configs_dict=get_configs("src/xuance_config/duel_dqn_config.yaml")
    configs=argparse.Namespace(**configs_dict)

    envs=make_envs(config=configs)
    agent=DuelDQN_Agent(config=configs, envs=envs)
    agent.train(configs.running_steps//configs.parallels)
    agent.save_model("duel_dqn_model.pth")
    agent.finish()