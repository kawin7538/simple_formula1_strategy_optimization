from tensorflow.keras.utils import plot_model

from f1_env.f1_env import F1Env
from main_f1_env_doubledqn_tensorflow import DQNAgent
from main_f1_env_duelingdqn_tensorflow import DuelingDQNAgent

f1_env=F1Env()
agent=DQNAgent(f1_env)
plot_model(agent.online_network, to_file="output/model_viz/dqn_network.png",show_shapes=True, show_layer_activations=True)
agent=DuelingDQNAgent(f1_env)
plot_model(agent.online_network, to_file="output/model_viz/dueling_dqn_network.png",show_shapes=True, show_layer_activations=True)