
import os
import visuals as vs

abs_path = os.path.dirname(os.path.abspath(__file__))

vs.plot_trials(os.path.join(abs_path, 'smartcab', 'logs', 'sim_improved-learning.csv'))


