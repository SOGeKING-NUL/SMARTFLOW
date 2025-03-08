from stable_baselines3 import PPO

class TrafficRLAgent:
    def __init__(self, env):
        self.model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            device="cpu",
            n_steps=1024,
            batch_size=64,
            learning_rate=3e-4,
            gamma=0.99
        )
    
    def predict_action(self, state):
        return self.model.predict(state)[0]
    
    def save(self, path):
        self.model.save(path)
    
    def load(self, path):
        self.model = PPO.load(path)