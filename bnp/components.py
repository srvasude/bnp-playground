import numpy as np
import inspect

class InfiniteArray():
    def __init__(self, f):
        self.values = {}
        self.f = f
    
    def __getitem__(self, indices):
        if indices not in self.values:
            self.values[indices] = self.f(*indices) if isinstance(indices, tuple) else self.f(indices)
        return self.values[indices]

def GEM(alpha):
    # Stick-breaking construction of the GEM.
    # alpha is the concentration parameter.
    betas = InfiniteArray(lambda i: np.random.beta(1, alpha))

    def draw():
        u = np.random.uniform()
        p = 0.0
        n = 0
        while p < u:
            p += betas[n] * (1 - p)
            n += 1
        return (n - 1)

    return draw

def DP(alpha, H):
    probs = GEM(alpha)
    atoms = InfiniteArray(lambda i: H())
    return (lambda: atoms[probs()])


def get_latents(data, already_cached=None, path=()):
    if already_cached is None:
        already_cached = dict()
        
    # Idea here is to recursively traverse the closed-over variables,
    # and extract latents. We do not want to store the same latent twice.
    if id(data) in already_cached:
        return already_cached[id(data)]
    
    if isinstance(data, InfiniteArray):
        d = {k: get_latents(v, already_cached, path=path + (k,)) for (k,v) in data.values.items()} | get_latents(data.f, already_cached, path=path)
        already_cached[id(data)] = path
        return d
    
    if callable(data):
        latent_variables = inspect.getclosurevars(data).nonlocals
        d = {key: (get_latents(value, already_cached, path=path + (key,)) if id(value) not in already_cached else already_cached[id(value)]) for (key, value) in latent_variables.items()}
        already_cached[id(data)] = path
        return d
    
    if isinstance(data, bool) or isinstance(data, int) or isinstance(data, float) or isinstance(data, str):
        return data
    
    already_cached[id(data)] = path
    return data

    

import rich
def print_sample(data):
    rich.print(get_latents(data))