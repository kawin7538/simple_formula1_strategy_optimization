"""
Dueling Double Deep Q Learning with Experience Replay
"""

import warnings
warnings.filterwarnings("ignore")

import os
import shutil
from itertools import product
from collections import deque
import random
from datetime import timedelta
import numpy as np
import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.losses import Huber
from tensorflow.keras.optimizers import Adam

from tqdm import tqdm

from f1_env.f1_env import F1Env
from models.car import Car
from models.racetrack import RaceTrack
from models.f1_simulation import F1Simulation
from utils.visualization import F1SimVisualization

BATCH_SIZE=128
MEMORY_SIZE=66*28*5
MAX_EPISODES=10000
MAX_STEPS=66*28
REWARD_DISCOUNT_FACTOR=0.95
TARGET_NETWORK_UPDATE_INTERVAL=28*10
epsilon=1
epsilon_decay_factor=0.999
epsilon_min=0.01

class DuelingDQNAgent:
    def __init__(self,env) -> None:
        self.env=env

        self.shape_observation_space=self.env.observation_space.shape
        num_action_space=[env.action_space[i].n for i in range(self.env.action_space.shape[0])]
        self.list_action_space=list(product(*[list(range(i)) for i in num_action_space]))

        self.sars_memory=deque(maxlen=MEMORY_SIZE)

        self.online_network=self.build_model()
        self.target_network=self.build_model()

    def build_model(self):
        input_layer=Input(shape=self.shape_observation_space)
        x=Dense(1024,activation='relu')(input_layer)
        x=Dense(1024,activation='relu')(x)
        action_layer=Dense(len(self.list_action_space),activation='softplus')(x)
        value_layer=Dense(1,activation='relu')(x)
        Q_layer=value_layer+tf.subtract(action_layer,tf.reduce_mean(action_layer,axis=1,keepdims=True))

        model=Model(input_layer,Q_layer)
        model.compile(loss=Huber(),optimizer=Adam(lr=1e-4))

        return model

    def encode_action(self, action:tuple|list):
        action_copy=tuple(action)
        return self.list_action_space.index(action_copy)
    
    def decode_action(self,action_idx:int):
        return self.list_action_space[action_idx]
    
    def get_action(self, state:np.ndarray, eps:float=0.5):
        if np.random.rand()>eps:
            return np.argmax(self.online_network.predict([state.tolist()],verbose=False)[0])
        else:
            return self.encode_action(self.env.action_space.sample())
        
if __name__ == '__main__':
    f1_env=F1Env()
    agent=DuelingDQNAgent(f1_env)
    deque_episode_rewards=deque(maxlen=512)
    list_time_usage_overall=[]

    t=0
    
    for episode_idx in (pbar1:=tqdm(range(MAX_EPISODES))):
        state, info = f1_env.reset()
        episode_reward=0

        for step_idx in tqdm(range(MAX_STEPS),leave=False):
            action_idx=agent.get_action(state, eps=epsilon)
            decoded_action=agent.decode_action(action_idx)
            next_state, reward, terminated, truncated, info = f1_env.step(decoded_action)

            agent.sars_memory.append([state,action_idx,reward,next_state,terminated])

            episode_reward+=reward

            if len(agent.sars_memory)>=BATCH_SIZE:
                batch=np.array(random.sample(agent.sars_memory,BATCH_SIZE),dtype='object')
                target=batch[:,2]+REWARD_DISCOUNT_FACTOR*np.max(agent.target_network.predict(np.stack(batch[:,3]),verbose=False),axis=1)*(1-batch[:,4])
                current_Q=agent.target_network.predict(np.stack(batch[:,0]),verbose=False)
                current_Q[np.arange(BATCH_SIZE),list(batch[:,1])]=target
                agent.online_network.fit(np.stack(batch[:,0]),current_Q, batch_size=BATCH_SIZE,verbose=False)

            state=next_state

            epsilon=max(epsilon_min,epsilon*epsilon_decay_factor)

            if len(agent.sars_memory)>=BATCH_SIZE and t%TARGET_NETWORK_UPDATE_INTERVAL==0:
                agent.target_network.set_weights(agent.online_network.get_weights())

            t+=1

            if terminated:
                break;

        deque_episode_rewards.append(episode_reward)

        if f1_env.dnf:
            pbar1.set_postfix({
                'latest_reward':episode_reward,
                'avg_reward':sum(deque_episode_rewards)/len(deque_episode_rewards),
                'max_reward':max(deque_episode_rewards)
            })
        else:
            list_time_usage_overall.append(sum(f1_env.list_time_usage_all_stopwatches))
            pbar1.set_postfix({
                'latest_reward':episode_reward,
                'avg_reward':sum(deque_episode_rewards)/len(deque_episode_rewards),
                'max_reward':max(deque_episode_rewards),
                'fastest_time_usage':timedelta(seconds=min(list_time_usage_overall))
            })
            # create viz of race performance
            os.makedirs(f'output/dueling_dqn/race_performance/ep_{episode_idx}/',exist_ok=True)
            # f1_sim_obj=F1Simulation(Car(),RaceTrack(),66)
            # f1_sim_obj.initialize_setting(f1_env.list_tyre_setting_all_laps, f1_env.list_car_status_will_be_pit, f1_env.list_engine_setting_all_stopwatches, f1_env.list_brake_setting_all_stopwatches)
            # f1_sim_obj.race()
            f1_viz_obj=F1SimVisualization(f1_env)
            f1_viz_obj.plot_package(f'output/dueling_dqn/race_performance/ep_{episode_idx}/')
            if sum(f1_env.list_time_usage_all_stopwatches)==min(list_time_usage_overall):
                shutil.copytree(f'output/dueling_dqn/race_performance/ep_{episode_idx}/','output/dueling_dqn/race_performance/_best/',dirs_exist_ok=True)

        agent.online_network.save(f'output/dueling_dqn/model/ep_{episode_idx}.keras')