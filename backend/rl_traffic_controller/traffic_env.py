import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time

class TrafficSignalEnv(gym.Env):
    def __init__(self, density_source, signal_controller):
        super().__init__()
        self.density_source = density_source
        self.signal_controller = signal_controller
        
        # Define observation space
        self.observation_space = spaces.Box(
            low=0, 
            high=100, 
            shape=(4,),  # [density, phase_duration, ns_red_time, ew_red_time]
            dtype=np.float32
        )
        # Update observation space for 4 lanes
        self.observation_space = spaces.Box(
            low=0, 
            high=100, 
            shape=(4,),  # Densities for north, south, east, west
            dtype=np.float32
        )
        
        # Define action space
        self.action_space = spaces.Discrete(4)  # 4 possible phases
        
        # Timing parameters
        self.MIN_GREEN_TIME = 15
        self.MAX_RED_TIME = 120
        self.PHASE_DURATIONS = [30, 5, 30, 5]  # Green NS, Yellow, Green EW, Yellow
        
        # Initialize state
        self.current_phase = 0
        self.phase_start_time = time.time()
        self.phase_red_times = [0.0, 0.0]  # NS red time, EW red time

        # Define phase directions
        self.PHASE_DIRECTIONS = {
            0: ["north", "south"],  # NS green
            1: [],                  # All red (NS yellow)
            2: ["east", "west"],    # EW green
            3: []                   # All red (EW yellow)
        }
        self.allowed_directions = self.PHASE_DIRECTIONS[self.current_phase]


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_phase = 0
        self.phase_start_time = time.time()
        self.phase_red_times = [0.0, 0.0]
        self.density_source.reset()
        return self._get_state(), {}

    def _get_state(self):
        return np.array([
            self.density_source.lane_densities['north'],
            self.density_source.lane_densities['south'],
            self.density_source.lane_densities['east'],
            self.density_source.lane_densities['west']
        ], dtype=np.float32)

    def step(self, action):
        # Update phase timers
        current_time = time.time()
        time_delta = current_time - self.phase_start_time
        
        # Update red times for non-active phases
        if self.current_phase in [0, 3]:  # NS green/yellow
            self.phase_red_times[1] += time_delta
        else:  # EW green/yellow
            self.phase_red_times[0] += time_delta
            
        # Update allowed directions when phase changes
        if time_delta > self.PHASE_DURATIONS[self.current_phase]:
            self.current_phase = (self.current_phase + 1) % 4
            self.phase_start_time = current_time
            self.phase_red_times = [0.0, 0.0]
            self.allowed_directions = self.PHASE_DIRECTIONS[self.current_phase]
            
        # Get new state
        state = self._get_state()
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Check termination
        done = False
        return state, reward, done, False, {}

    def _calculate_reward(self):
        return self.density_source.density_percentage * 0.1  # Simple reward