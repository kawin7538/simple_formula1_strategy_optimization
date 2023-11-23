"""
Branching Dueling Double Deep Q Learning with Experience Replay and historical data
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
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization, GRU, Concatenate
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
INPUT_HISTORICAL_SIZE=28*10
MAX_EPISODES=10000
MAX_STEPS=66*28
REWARD_DISCOUNT_FACTOR=0.95
TARGET_NETWORK_UPDATE_INTERVAL=28*10
epsilon=1
epsilon_decay_factor=0.9999
epsilon_min=0.01

class BranchingDuelingDQNwithHistoricalAgent:
    def __init__(self,env) -> None:
        self.env=env

        self.shape_observation_space=self.env.observation_space.shape
        self.num_action_space=[env.action_space[i].n for i in range(self.env.action_space.shape[0])]
        # self.list_action_space=list(product(*[list(range(i)) for i in num_action_space]))

        self.sars_memory=deque(maxlen=MEMORY_SIZE)

        self.online_network=self.build_model()
        self.target_network=self.build_model()

    def build_model(self):
        input_state_layer=Input(shape=self.shape_observation_space,name='input_state_layer')
        input_historical_tyre_temperature_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1,),name='input_historical_tyre_temperature_layer')
        input_historical_tyre_reliability_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1,),name='input_historical_tyre_reliability_layer')
        input_historical_engine_temperature_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1,),name='input_historical_engine_temperature_layer')
        input_historical_engine_reliability_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1,),name='input_historical_engine_reliability_layer')
        input_historical_engine_horsepower_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1,),name='input_historical_engine_horsepower_layer')
        input_historical_engine_fuel_level_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1,),name='input_historical_engine_fuel_level_layer')
        input_historical_brake_temperature_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1),name='input_historical_brake_temperature_layer')
        input_historical_brake_pressure_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1,),name='input_historical_brake_pressure_layer')
        input_historical_brake_reliability_layer=Input(shape=(INPUT_HISTORICAL_SIZE,1,),name='input_historical_brake_reliability_layer')

        gru_historical_tyre_temperature_layer=GRU(128,name='gru_historical_tyre_temperature_layer')(input_historical_tyre_temperature_layer)
        gru_historical_tyre_reliability_layer=GRU(128,name='gru_historical_tyre_reliability_layer')(input_historical_tyre_reliability_layer)
        gru_historical_engine_temperature_layer=GRU(128,name='gru_historical_engine_temperature_layer')(input_historical_engine_temperature_layer)
        gru_historical_engine_reliability_layer=GRU(128,name='gru_historical_engine_reliability_layer')(input_historical_engine_reliability_layer)
        gru_historical_engine_horsepower_layer=GRU(128,name='gru_historical_engine_horsepower_layer')(input_historical_engine_horsepower_layer)
        gru_historical_engine_fuel_level_layer=GRU(128,name='gru_historical_engine_fuel_level_layer')(input_historical_engine_fuel_level_layer)
        gru_historical_brake_temperature_layer=GRU(128,name='gru_historical_brake_temperature_layer')(input_historical_brake_temperature_layer)
        gru_historical_brake_pressure_layer=GRU(128,name='gru_historical_brake_pressure_layer')(input_historical_brake_pressure_layer)
        gru_historical_brake_reliability_layer=GRU(128,name='gru_historical_brake_reliability_layer')(input_historical_brake_reliability_layer)

        input_concat_layer=Concatenate(name='input_concatenate_layer')([input_state_layer,gru_historical_tyre_temperature_layer,gru_historical_tyre_reliability_layer,gru_historical_engine_temperature_layer,gru_historical_engine_reliability_layer,gru_historical_engine_horsepower_layer,gru_historical_engine_fuel_level_layer,gru_historical_brake_temperature_layer,gru_historical_brake_pressure_layer,gru_historical_brake_reliability_layer])

        x=Dense(256,activation='relu')(input_concat_layer)
        x=Dense(256,activation='relu')(x)
        x=BatchNormalization()(x)
        fc1_tyre_set_layer=Dense(256,activation='relu',name='fc1_tyre_set_layer')(x)
        fc2_tyre_set_layer=Dense(256,activation='relu',name='fc2_tyre_set_layer')(fc1_tyre_set_layer)
        advantage_tyre_set_layer=Dense(self.num_action_space[0],activation='softplus',name='advantage_tyre_set_layer')(fc2_tyre_set_layer)
        fc1_pit_next_lap_layer=Dense(256,activation='relu',name='fc1_pit_next_lap_layer')(x)
        fc2_pit_next_lap_layer=Dense(256,activation='relu',name='fc2_pit_next_lap_layer')(fc1_pit_next_lap_layer)
        advantage_pit_next_lap_layer=Dense(self.num_action_space[1],activation='softplus',name='advantage_pit_next_lap_layer')(fc2_pit_next_lap_layer)
        fc1_engine_mode_layer=Dense(256,activation='relu',name='fc1_engine_mode_layer')(x)
        fc2_engine_mode_layer=Dense(256,activation='relu',name='fc2_engine_mode_layer')(fc1_engine_mode_layer)
        advantage_engine_mode_layer=Dense(self.num_action_space[2],activation='softplus',name='advantage_engine_mode_layer')(fc2_engine_mode_layer)
        fc1_brake_mode_layer=Dense(256,activation='relu',name='fc1_brake_mode_layer')(x)
        fc2_brake_mode_layer=Dense(256,activation='relu',name='fc2_brake_mode_layer')(fc1_brake_mode_layer)
        advantage_brake_mode_layer=Dense(self.num_action_space[3],activation='softplus',name='advantage_brake_mode_layer')(fc2_brake_mode_layer)
        fc1_value_layer=Dense(256,activation='relu',name='fc1_value_layer')(x)
        fc2_value_layer=Dense(256,activation='relu',name='fc2_value_layer')(fc1_value_layer)
        value_layer=Dense(1,activation='relu',name='value_layer')(fc2_value_layer)
        Q_tyre_set_layer=tf.add(value_layer,tf.subtract(advantage_tyre_set_layer,tf.reduce_mean(advantage_tyre_set_layer,axis=1,keepdims=True,name='advantage_tyre_set_mean_layer'),name='advantage_tyre_set_subtract_layer'),name='Q_tyre_set_layer')
        Q_pit_next_lap_layer=tf.add(value_layer,tf.subtract(advantage_pit_next_lap_layer,tf.reduce_mean(advantage_pit_next_lap_layer,axis=1,keepdims=True,name='advantage_pit_next_lap_mean_layer'),name='advantage_pit_next_lap_subtract_layer'),name='Q_pit_next_lap_layer')
        Q_engine_mode_layer=tf.add(value_layer,tf.subtract(advantage_engine_mode_layer,tf.reduce_mean(advantage_engine_mode_layer,axis=1,keepdims=True,name='advantage_engine_mode_mean_layer'),name='advantage_engine_mode_subtract_layer'),name='Q_engine_mode_layer')
        Q_brake_mode_layer=tf.add(value_layer,tf.subtract(advantage_brake_mode_layer,tf.reduce_mean(advantage_brake_mode_layer,axis=1,keepdims=True,name='advantage_brake_mode_mean_layer'),name='advantage_brake_mode_subtract_layer'),name='Q_brake_mode_layer')

        model=Model([input_state_layer,input_historical_tyre_temperature_layer,input_historical_tyre_reliability_layer,input_historical_engine_temperature_layer,input_historical_engine_reliability_layer,input_historical_engine_horsepower_layer,input_historical_engine_fuel_level_layer,input_historical_brake_temperature_layer,input_historical_brake_pressure_layer,input_historical_brake_reliability_layer],[Q_tyre_set_layer,Q_pit_next_lap_layer,Q_engine_mode_layer,Q_brake_mode_layer])
        model.compile(loss='mean_squared_error',optimizer='adam')

        return model

    def encode_action(self, action:tuple|list):
        action_copy=tuple(action)
        return self.list_action_space.index(action_copy)
    
    def decode_action(self,action_idx:int):
        return self.list_action_space[action_idx]
    
    def get_action(self, state:np.ndarray, historical_data:list, eps:float=0.5):
        if np.random.rand()>eps:
            q_predicted=self.online_network.predict([state.tolist(),*historical_data],verbose=False)
            return np.array([np.argmax(q_predicted[i][0]) for i in range(4)])
        else:
            return self.env.action_space.sample()
        

def modify_historical_data(historical_data:list):
    copy_historical_data=historical_data.copy()
    copy_historical_data=[i for i in copy_historical_data if i is not None]
    copy_historical_data=([np.nan]*INPUT_HISTORICAL_SIZE)+copy_historical_data
    return copy_historical_data[-INPUT_HISTORICAL_SIZE:]

def get_historical_data(f1_env:F1Env):
    return modify_historical_data(f1_env.list_tyre_temperature_all_stopwatches), modify_historical_data(f1_env.list_tyre_reliability_all_stopwatches), modify_historical_data(f1_env.list_engine_temperature_all_stopwatches), modify_historical_data(f1_env.list_engine_reliability_all_stopwatches), modify_historical_data(f1_env.list_engine_horsepower_all_stopwatches), modify_historical_data(f1_env.list_engine_fuel_level_all_stopwatches), modify_historical_data(f1_env.list_brake_temperature_all_stopwatches), modify_historical_data(f1_env.list_brake_pressure_all_stopwatches), modify_historical_data(f1_env.list_brake_reliability_all_stopwatches)

if __name__ == '__main__':
    f1_env=F1Env()
    agent=BranchingDuelingDQNwithHistoricalAgent(f1_env)
    deque_episode_rewards=deque(maxlen=512)
    list_time_usage_overall=[]

    t=0
    
    for episode_idx in (pbar1:=tqdm(range(MAX_EPISODES))):
        state, info = f1_env.reset()
        episode_reward=0

        for step_idx in tqdm(range(MAX_STEPS),leave=False):
            historical_data=get_historical_data(f1_env)
            action=agent.get_action(state,historical_data,eps=epsilon)
            next_state, reward, terminated, truncated, info = f1_env.step(action)
            next_historical_data=get_historical_data(f1_env)

            agent.sars_memory.append([state,action,reward,next_state,terminated,historical_data,next_historical_data])

            episode_reward+=reward

            if len(agent.sars_memory)>=BATCH_SIZE:
                batch=np.array(random.sample(agent.sars_memory,BATCH_SIZE),dtype='object')
                historical_data=np.stack(batch[:,5],axis=1)
                next_historical_data=np.stack(batch[:,6],axis=1)
                list_input_target_q=[np.stack(batch[:,3])]
                for i in next_historical_data:
                    list_input_target_q.append(i)
                target_q_predicted=agent.target_network.predict(list_input_target_q,verbose=False)
                max_target_q_predicted=[np.max(q_predicted,axis=1) for q_predicted in target_q_predicted]
                mean_max_target_q_predicted=np.mean(max_target_q_predicted,axis=0)
                target=batch[:,2]+REWARD_DISCOUNT_FACTOR*mean_max_target_q_predicted*(1-batch[:,4])
                list_input_current_q=[np.stack(batch[:,0])]
                for i in historical_data:
                    list_input_current_q.append(i)
                current_Q=agent.target_network.predict(list_input_current_q,verbose=False)
                for i in range(f1_env.action_space.shape[0]):
                    list_action_over_batch=[batch[:,1][j][i] for j in range(BATCH_SIZE)]
                    current_Q[i][np.arange(BATCH_SIZE),list_action_over_batch]=target
                agent.online_network.fit(list_input_current_q,current_Q,batch_size=BATCH_SIZE, verbose=False)

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
            os.makedirs(f'output/branching_dueling_dqn_with_historical/race_performance/ep_{episode_idx}/',exist_ok=True)
            f1_viz_obj=F1SimVisualization(f1_env)
            f1_viz_obj.plot_package(f'output/branching_dueling_dqn_with_historical/race_performance/ep_{episode_idx}/')
            if sum(f1_env.list_time_usage_all_stopwatches)==min(list_time_usage_overall):
                shutil.copytree(f'output/branching_dueling_dqn_with_historical/race_performance/ep_{episode_idx}/','output/branching_dueling_dqn_with_historical/race_performance/_best/',dirs_exist_ok=True)

        agent.online_network.save(f'output/branching_dueling_dqn_with_historical/model/ep_{episode_idx}.keras')