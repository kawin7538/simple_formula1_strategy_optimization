# To install Xuance
- conda create with python=3.10
- conda install -c intel mpi4py
- pip install requirements.txt
- pip install --upgrade torch
- change "agent.py" in xuance/torch/agent/ line 87 from "form" to "thread"