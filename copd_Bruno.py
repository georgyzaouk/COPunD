from cellularautomata import CountType, GuiCA
from random import random

# Condition
CONDITION: str = 'control'

# TIME SCALE
K_TIME = 10

# Constants
P_MOVE_C = 0.2
P_MOVE_F = 0.5

CURRENT_STEP = 0


# Scaling helper
def _scale(p: float, k: int = K_TIME) -> float:
    return 1.0 - (1.0 - p) ** k


# Cohesion (anti-diffusion)
def cohesion(n_same: int) -> float:
    # isolates move more, clusters move less
    return 1.0 / (1.0 + (n_same ** 1.5))


# Cluster attraction (phase separation force)
def cluster_attraction(n_same: int) -> float:
    # increases mobility bias toward dense regions
    return 0.3 + 0.7 * (n_same / 8.0)


# Parameters
def build_params():

    p_F_die_base = 4.8e-4
    p_C_die_base = 8.0e-4

    return {

        # death
        'p_F_die': _scale(p_F_die_base),
        'p_C_die': _scale(p_C_die_base),

        # fibrocyte infiltration
        'p_F_infil': (
            _scale(p_F_die_base * 0.3) if CONDITION == 'COPD' else 0.0
        ),

        # CD8 birth (fibrocyte-dependent ONLY)
        'p_C_birth': (
            _scale(2.0e-3) if CONDITION == 'COPD' else _scale(1.0e-4)
        ),
    }


PARAMS = build_params()


# Update rule
def CopdPCA(cell, neighbors: list):

    global CURRENT_STEP

    p = PARAMS
    category, status = cell

    active_neighbors = [n for n in neighbors if n[1] != 'migrating']

    n_F = CountType(active_neighbors, 'Fibrocyte')
    n_C = CountType(active_neighbors, 'CD8')

    match category:
        # EMPTY
        case 'Empty':

            # fibrocyte infiltration
            if random() < p['p_F_infil']:
                return ('Fibrocyte', None)

            # CD8 birth ONLY if fibrocyte nearby
            if n_F > 0:
                if random() < p['p_C_birth']:
                    return ('CD8', None)

            return cell

        # FIBROCYTE
        case 'Fibrocyte':

            if random() < p['p_F_die']:
                return ('Empty', None)

            n_same = n_F

            # mobility = diffusion × cohesion × attraction
            mobility = P_MOVE_F
            mobility *= cohesion(n_same)
            mobility *= cluster_attraction(n_same)

            if random() < mobility:
                return ('Fibrocyte', 'migrating')

            return ('Fibrocyte', None)

        # CD8
        case 'CD8':

            if random() < p['p_C_die']:
                return ('Empty', None)

            n_same = n_C

            mobility = P_MOVE_C
            mobility *= cohesion(n_same)
            mobility *= cluster_attraction(n_same)

            if random() < mobility:
                return ('CD8', 'migrating')

            return ('CD8', None)

    return cell


# Colors
cellcolors = {
    ('Empty', None): 'whitesmoke',
    ('Fibrocyte', None): '#27ae60',
    ('CD8', None): '#e91e8c',
}


# Run
if __name__ == '__main__':

    print(f"COPD CA running in '{CONDITION}' mode (cluster-physics enabled)")

    def wrapped_rule(cell, neighbors):
        global CURRENT_STEP
        out = CopdPCA(cell, neighbors)
        CURRENT_STEP += 1
        return out

    GuiCA(
        wrapped_rule,
        cellcolors,
        figheight=5,
        gridsize=100,
        duration=600,
    )