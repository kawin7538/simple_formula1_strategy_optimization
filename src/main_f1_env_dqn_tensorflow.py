"""
Double Deep Q Learning with Experience Replay
"""

from itertools import product
from datetime import timedelta
import numpy as np
from tensorflow.keras import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam

from tqdm import tqdm

from f1_env.f1_env import F1Env

class DQNAgent:
    def __init__(self,env) -> None:
        self.env=env

        self.shape_observation_space=self.env.observation_space.shape
        num_action_space=[env.action_space[i].n for i in range(self.env.action_space.shape[0])]
        self.list_action_space=list(product(*[list(range(i)) for i in num_action_space]))

        self.online_network=self.build_model()
        self.target_network=self.build_model()

    def build_model(self):
        input_layer=Input(shape=(12,))
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
    
    def get_action(self, state:tuple|list, eps:float=0.5):
        if np.random.rand()>eps:
            print(state)
            return np.argmax(self.online_network.predict(state,verbose=False)[0])
        else:
            return self.encode_action(self.env.action_space.sample())

    def compute_loss(self, batch):
        pass;

    def update(self, batch_size):
        pass;

if __name__ == '__main__':
    f1_env=F1Env()
    agent=DQNAgent(f1_env)
    episode_rewards=[]
    
    for episode in tqdm(range((max_episodes:=10000))):
        state, info = f1_env.reset()
        episode_reward=0

        for step in range((max_steps:=66*28)):
            print(state)
            action_idx=agent.get_action(state)
            print(action_idx)
            decoded_action=agent.decode_action(action_idx)
            print(decoded_action)
            next_state, reward, terminated, truncated, info = f1_env.step(decoded_action)