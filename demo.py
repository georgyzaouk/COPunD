"""
Demo for the COPD CA model — runs both conditions without the CA GUI.

Generates initial states for control and COPD, runs the synchronous CA
simulation in each, and saves:
  - {key1}_counts.png    — population of F and C over time, both conditions
  - {key1}_snapshots.png — start vs final state, both conditions
  - {key1}_{condition}.gif — animation of the simulation

Usage:
    python demo.py
"""

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from random import seed as set_seed
import os

from cellularautomata import GenerateCA, SimulateCA, ShowSimulation
import copd_Bruno as copd_pca



# Settings
# =========
GRIDSIZE = 50
DURATION = 300
SEED = 42

# Initial weights match the paper's density: ~3% C, ~0.5% F, ~96.5% Empty
INIT_WEIGHTS = {'Empty': 0.965, 'Fibrocyte': 0.005, 'CD8': 0.030}


# Helpers
# ========
def count_cells(grid):
    """
        Returns (n_F, n_C) for a 2D cell-tuple grid.
    """
    n_F = n_C = 0
    for row in grid:
        for cell in row:
            if cell[0] == 'Fibrocyte':
                n_F += 1
            elif cell[0] == 'CD8':
                n_C += 1
    return n_F, n_C


def grid_to_image(grid):
    """
        Convert a 2D cell-tuple grid to an integer image for imshow.
    """
    type_to_idx = {'Empty': 0, 'Fibrocyte': 1, 'CD8': 2}
    n = len(grid)
    img = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            img[i, j] = type_to_idx.get(grid[i][j][0], 0)
    return img


def run(condition, value):
    """
        Run a simulation in the given condition. Returns the simulation trace.
    """
    copd_pca.CONDITION = condition
    copd_pca.K_TIME = value
    copd_pca.PARAMS = copd_pca.build_params()
    set_seed(SEED)
    np.random.seed(SEED)
    ca0 = GenerateCA(GRIDSIZE, copd_pca.cellcolors, INIT_WEIGHTS)
    return SimulateCA(ca0, copd_pca.CopdPCA, duration=DURATION)


# Main
# =====
def main():
    print(f"COPD CA Demo — {GRIDSIZE}x{GRIDSIZE} grid, {DURATION} steps\n")
    tests = {'12days': 1, '125days': 10, '250days': 20, '625days': 50}

    cellcolors = {
        ('Empty',     None): 'whitesmoke',
        ('Fibrocyte', None): '#27ae60',   # green — fibrocyte
        ('CD8',       None): '#e91e8c',   # pink  — CD8+ T lymphocyte
    }

    colors = {'control': '#27ae60', 'COPD': '#e91e8c'} # is it pink?

    for key1, value in tests.items():
        # Runs the CA for each timescaled conditions
        results = {}
        os.makedirs(f"Project/{key1}", exist_ok=True)
        for condition in ('control', 'COPD'):
            print(f"Running {condition}...")
            sim = run(condition, value)
            anim = ShowSimulation(sim, cellcolors)
            anim.save(f'Project/{key1}/{key1}_{condition}.gif', writer='pillow', fps=10)

            F_traj = [count_cells(s)[0] for s in sim]
            C_traj = [count_cells(s)[1] for s in sim]
            results[condition] = {'sim': sim, 'F': F_traj, 'C': C_traj}

            # Average over last 20% of steps as a steady-state estimate
            tail = DURATION // 5
            avg_F = sum(F_traj[-tail:]) / tail
            avg_C = sum(C_traj[-tail:]) / tail
            print(f"  initial: F={F_traj[0]:>3d}  C={C_traj[0]:>3d}")
            print(f"  final:   F={F_traj[-1]:>3d}  C={C_traj[-1]:>3d}")
            print(f"  last {tail}-step mean: F={avg_F:.0f}  C={avg_C:.0f}\n")

        # Plot population over time
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        for ax, key in zip(axes, ['F', 'C']):
            for condition in ('control', 'COPD'):
                ax.plot(results[condition][key], color=colors[condition],
                        label=condition, lw=1.5)
            ax.set_xlabel('step')
            ax.set_ylabel(f"N({key})")
            ax.set_title(f"{'Fibrocyte' if key=='F' else 'CD8'} count over time")
            ax.legend(loc='best')
            ax.grid(alpha=0.3)
        fig.suptitle(f"COPunD: synchronous-update simplification of Dupin et al. (2023) - K={value}",
                     fontsize=10)
        plt.tight_layout()
        plt.savefig(f'Project/{key1}/{key1}_counts.png', dpi=120)

        # Snapshots
        cmap = ListedColormap(['whitesmoke', '#27ae60', '#e91e8c'])
        fig, axes = plt.subplots(2, 2, figsize=(9, 9))
        for row, condition in enumerate(('control', 'COPD')):
            for col, idx in enumerate([0, -1]):
                ax = axes[row, col]
                img = grid_to_image(results[condition]['sim'][idx])
                ax.imshow(img, cmap=cmap, vmin=-0.5, vmax=2.5, interpolation='nearest')
                ax.set_xticks([])
                ax.set_yticks([])
                label = 'initial' if idx == 0 else f'step {DURATION}'
                ax.set_title(f"{condition} — {label}")
        plt.tight_layout()
        plt.savefig(f'Project/{key1}/{key1}_snapshots.png', dpi=120)


if __name__ == '__main__':
    main()