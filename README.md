# COPunD

**COPunD** is a simplified cellular automaton model inspired by the work of Dupin et al. (2023) on fibrocyte and CD8+ T-cell interactions in Chronic Obstructive Pulmonary Disease (COPD).

The objective of this project is to reproduce, in a simplified way, how local interactions between fibrocytes and CD8+ T lymphocytes may lead to different spatial patterns in healthy and COPD-like tissue conditions.

## Project Overview

This model is based on a probabilistic cellular automaton. Each site of the grid can be in one of three states:

- `Empty`
- `Fibrocyte`
- `CD8`

The model compares two conditions:

- `control`: represents healthy tissue
- `COPD`: represents diseased tissue with stronger inflammatory behavior

The COPD condition includes increased fibrocyte infiltration and CD8 cell proliferation, allowing the simulation to reproduce progressive inflammatory cell accumulation over time.

## Repository Structure

```text
COPunD/
│
├── cellularautomata.py     # Course cellular automata framework
├── copd_Bruno.py           # Main COPD cellular automaton model
├── demo.py                 # Script running simulations and saving results
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
└── Project/
    ├── 12days/
    │   ├── 12days_counts.png
    │   ├── 12days_snapshots.png
    │   ├── 12days_control.gif
    │   └── 12days_COPD.gif
    │
    ├── 125days/
    │   ├── 125days_counts.png
    │   ├── 125days_snapshots.png
    │   ├── 125days_control.gif
    │   └── 125days_COPD.gif
    │
    ├── 250days/
    │   ├── 250days_counts.png
    │   ├── 250days_snapshots.png
    │   ├── 250days_control.gif
    │   └── 250days_COPD.gif
    │
    └── 625days/
        ├── 625days_counts.png
        ├── 625days_snapshots.png
        ├── 625days_control.gif
        └── 625days_COPD.gif
