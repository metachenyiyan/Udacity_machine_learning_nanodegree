import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)  # Set the agent in the evironment
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning  # Whether the agent is expected to learn

        self.epsilon = epsilon  # Random exploration factor
        self.alpha = alpha  # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.Q = dict() # Create a Q-table which will be a dictionary of tuples
        self.previous_sar = None
        self.n_trial = 0

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)

        ###########
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        self.n_trial += 1
        self.previous_sar = None
        if testing:
            self.n_trial -= 1
            self.epsilon = 0
            self.alpha = 0
        else:
            #self.epsilon = pow(2.71828, -0.001*self.n_trial)
            # if random.random() < 0.9:
            #      self.n_trial -= 1
            # self.epsilon = 1.0/(self.n_trial*self.n_trial + 1)
            self.epsilon -= 0.05
            #self.epsilon = math.cos(0.01 * self.n_trial)
            #self.epsilon = math.cos(0.000157079*self.n_trial)
            #self.alpha = 1.0/(self.n_trial + 1)

    def build_state(self):
        """ The build_state function is called when the agent requests data from the
            environment. The next waypoint, the intersection inputs, and the deadline
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint()  # The next waypoint
        inputs = self.env.sense(self)  # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ###########
        ## TO DO ##
        ###########

        # NOTE : you are not allowed to engineer features outside of the inputs available.
        # Because the aim of this project is to teach Reinforcement Learning, we have placed
        # constraints in order for you to learn hApproximately how many training trials did the driving agent require before testing? Does that number make sense given ow to adjust epsilon and alpha, and thus learn about the balance between exploration and exploitation.
        # With the hand-engineered features, this learning process gets entirely negated.

        # Set 'state' as a tuple of relevant data for the agent
        state = (waypoint, inputs['light'], inputs['oncoming'], inputs['left'])

        return state

    def get_maxQ(self, state):
        """ The get_maxQ function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ###########
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
        max_value = max(value for value in self.Q[state].values())
        candidates = [(value, key) for key, value in self.Q[state].items() if value == max_value]
        maxQ, action = random.choice(candidates)
        if action == "none":
            action = None
        return maxQ, action

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ###########
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
        if state not in self.Q:
            self.Q[state] = dict()
            self.Q[state]["right"] = 0.0
            self.Q[state]["left"] = 0.0
            self.Q[state]["forward"] = 0.0
            self.Q[state]["none"] = 0.0

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        if not self.learning:
            action = random.choice(self.valid_actions)
        else:
            if random.random() < self.epsilon:
                action = random.choice(self.valid_actions)
            else:
                action = self.get_maxQ(state)[1]
        return action

    def learn(self, new_state):
        """ The learn function is called after the agent completes an action and
            receives a reward. This function does not consider future rewards
            when conducting learning. """

        ###########
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')

        if self.previous_sar:
            previous_state = self.previous_sar[0]
            previous_action = self.previous_sar[1]
            previous_reward = self.previous_sar[2]
            if not previous_action:
                previous_action = "none"
            action2value = self.Q[previous_state]
            init_value = action2value[previous_action]
            new_value = previous_reward + self.get_maxQ(new_state)[0]
            action2value[previous_action] = init_value * (1 - self.alpha) + self.alpha * new_value

    def end_state_learn(self, state, action, reward):
        action2value = self.Q[state]
        if not action:
            action = "none"
        init_value = action2value[action]
        new_value = reward
        action2value[action] = init_value * (1 - self.alpha) + self.alpha * new_value

    def update(self):
        """ The update function is called when a time step is completed in the
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()  # Get current state
        self.createQ(state)  # Create 'state' in Q-table
        self.learn(state)  # Q-learn
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action)  # Receive a reward
        if self.env.done or state[-1] == 1: #episod ends
            self.end_state_learn(state, action, reward)
        else:
            self.previous_sar = (state, action, reward)


def run():
    """ Driving function for running the simulation.
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()

    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, learning=True)

    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, log_metrics=True, update_delay=0, display=False, optimized=False)

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=10, tolerance=0.00001)

    print agent.Q
    print len(agent.Q)
    print agent.n_trial
if __name__ == '__main__':
    run()
