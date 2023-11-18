"""
Double Deep Q Learning with Experience Replay
"""

from itertools import product
from collections import deque
import random
from datetime import timedelta
import numpy as np
from tensorflow.keras import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam

from tqdm import tqdm

from f1_env.f1_env import F1Env

BATCH_SIZE=256
MEMORY_SIZE=66*28*3
MAX_EPISODES=10000
MAX_STEPS=66*28
REWARD_DISCOUNT_FACTOR=0.99
TARGET_NETWORK_UPDATE_INTERVAL=28*10
epsilon=1
epsilon_decay_factor=0.99
epsilon_min=0.01

class DQNAgent:
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
        output_layer=Dense(len(self.list_action_space),activation='relu')(x)

        model=Model(input_layer, output_layer)
        model.compile(loss='mean_squared_error',optimizer=Adam(learning_rate=0.001))

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

    def compute_loss(self, batch):
        pass;

    def update(self, batch_size):
        pass;

if __name__ == '__main__':
    f1_env=F1Env()
    agent=DQNAgent(f1_env)
    list_episode_rewards=[]
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

            if t%TARGET_NETWORK_UPDATE_INTERVAL==0:
                agent.target_network.set_weights(agent.online_network.get_weights())

            t+=1

            if terminated:
                break;

        list_episode_rewards.append(episode_reward)

        if f1_env.dnf:
            list_time_usage_overall.append(1e9)
        else:
            list_time_usage_overall.append(sum(f1_env.list_time_usage_all_stopwatches))

        pbar1.set_postfix({
            'latest_reward':episode_reward,
            'avg_reward':sum(list_episode_rewards)/len(list_episode_rewards),
            'max_reward':max(list_episode_rewards),
            'fastest_time_usage':timedelta(seconds=min(list_time_usage_overall))
        })

        if episode_idx%20==0:
            agent.online_network.save(f'output/dqn/ep_{episode_idx}.h5')