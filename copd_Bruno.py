from cellularautomata import CountType, GuiCA
from random import random

# Conditions of the simulation
# ================================
# - 'control' : healthy tissue
# - 'COPD'    : diseased tissue
# COPD mode allows fibrocyte infiltration and stronger CD8 growth
# Basically: peaceful lungs vs lungs after years of cigarettes
CONDITION: str = 'control'


# Timescaling
# ============
# K_TIME accelerates biological processes.
# If 1 micro-step = 1 hour:
#   K_TIME = 1   -> slow biological evolution
#   K_TIME = 10  -> 10 hours compressed into one CA update
# Higher K_TIME = faster disease progression...
K_TIME = 10


# Constants
# ==========
# Fibrocytes move more than CD8 cells
P_MOVE_C = 0.2
P_MOVE_F = 0.5

# Global simulation counter
CURRENT_STEP = 0


# Methods
# ==========
# Scaling helper
def _scale(p: float, k: int = K_TIME) -> float:
    """
        Convert a probability defined at micro-time scale into a macro-time probability.
        Formula:
            1 - (1 - p)^k
        This is the probability that an event happens at least once
        during k independent substeps.
    """
    return 1.0 - (1.0 - p) ** k


# Cohesion function (anti-diffusion effect)
def cohesion(n_same: int) -> float:
    """
        Reduce mobility when surrounded by cells of the same type.
        Informations from the paper : 
        - isolated cells move a lot
        - clustered cells stay together
        Goal here is to avoid diffusion everywhere
    """
    return 1.0 / (1.0 + (n_same ** 1.5))


# Cluster attraction force
def cluster_attraction(n_same: int) -> float:
    """
        Add attraction toward dense regions.
        More neighbors of the same type lead stronger local aggregation tendency.
        New classmate integrating the bigger friend group ahh
    """
    return 0.3 + 0.7 * (n_same / 8.0)


# Parameters
def build_params():

    # Base death probabilities
    p_F_die_base = 4.8e-4
    p_C_die_base = 8.0e-4

    return {
        # Death probabilities
        # Time-scaled using K_TIME
        'p_F_die': _scale(p_F_die_base),
        'p_C_die': _scale(p_C_die_base),

        # Fibrocyte infiltration is only active in COPD mode
        # Local tissue brings fibrocytes
        'p_F_infil': (
            _scale(p_F_die_base * 0.3)
            if CONDITION == 'COPD'
            else 0.0
        ),

        # CD8 cells cannot appear alone
        # A fibrocyte must be nearby to trigger the creation of a new CD8 cell
        # -> inflammation
        'p_C_birth': (
            _scale(2.0e-3)
            if CONDITION == 'COPD'
            else _scale(1.0e-4)
        ),
    }


# Build parameter dictionary
PARAMS = build_params()


# Main update rule
def CopdPCA(cell, neighbors: list):
    global CURRENT_STEP
    p = PARAMS

    # Current cell information
    category, status = cell

    # Ignore migrating cells when computing local statistics
    active_neighbors = [
        n for n in neighbors
        if n[1] != 'migrating'
    ]

    # Count neighboring fibrocytes and CD8 cells
    n_F = CountType(active_neighbors, 'Fibrocyte')
    n_C = CountType(active_neighbors, 'CD8')

    # Cell behavior depends on its category
    match category:

        # EMPTY CELL
        case 'Empty':
            # New fibrocytes may enter the tissue
            if random() < p['p_F_infil']:
                return ('Fibrocyte', None)

            # CD8 can ONLY appear if a fibrocyte is nearby
            # No fibrocyte:
            # -> no inflammatory signal
            # -> no CD8 proliferation
            # Prevents spontaneous CD8 explosions...
            if n_F > 0:
                if random() < p['p_C_birth']:
                    return ('CD8', None)

            return cell

        # FIBROCYTE
        case 'Fibrocyte':
            # Death
            if random() < p['p_F_die']:
                return ('Empty', None)

            # Mobility depends on:
            # - its probability
            # - cohesion (less movement inside clusters)
            # - attraction toward dense regions
            # -> Fibrocytes form visible aggregates !
            n_same = n_F
            mobility = P_MOVE_F
            mobility *= cohesion(n_same)
            mobility *= cluster_attraction(n_same)

            # Migration attempt
            if random() < mobility:
                return ('Fibrocyte', 'migrating')

            return ('Fibrocyte', None)

        # CD8 CELL
        case 'CD8':
            # Death
            if random() < p['p_C_die']:
                return ('Empty', None)

            # Same clustering logic as fibrocytes
            # CD8 cells become less mobile inside dense CD8 clusters
            n_same = n_C
            mobility = P_MOVE_C
            mobility *= cohesion(n_same)
            mobility *= cluster_attraction(n_same)

            # Migration attempt
            if random() < mobility:
                return ('CD8', 'migrating')

            return ('CD8', None)

    # Safety fallback
    return cell


# Color map
cellcolors = {
    ('Empty', None): 'whitesmoke',
    ('Fibrocyte', None): '#27ae60',
    ('CD8', None): '#e91e8c', # is it pink?
}


# Run simulation
if __name__ == '__main__':
    print(f"COPD CA running in '{CONDITION}' mode ")

    # Wrapper used to increment global simulation time
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
