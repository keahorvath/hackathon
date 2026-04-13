# PMS hackathon: guide for CPMpy

## Installation

To use Python and CPMpy to solve the problem, you should first make sure you have a recent python version (I used 3.12 for development).

You should then prepare your Python environment and install `cpmpy` with `pip` :

```
pip install cpmpy
```

You should also make sure you have `blockviz` and the PMS library installed on your computer :

```
pip install git+https://gitlab.laas.fr/roc/titouan-seraud/blockviz.git
pip install git+https://gitlab.laas.fr/roc/titouan-seraud/pms.git
```

## Usage

You can copy and use the `cpmpy_template.py` file to quickly start modeling and solving the problem using the CPMpy library and OR-Tools solver. It contains functions to open data, create the variables of the problem, the objective function, solve the problem, and visualize its solutions with blockviz.

Once you created your model, you can use the `blockviz` to visualize your solutions in real-time :

```
python my-cpmpy-solver.py | blockviz
```

You can also redirect the solver output to a file to visualize the solution step-by-step :

```
python my-cpmpy-solver.py > trace.json
blockviz trace.json
```

The solve function is compatible with `blockviz` but it only works with the ORTools solver. You can personalize the ORTools solver parameters as you want, and also access the sovler's logs.

Feel free to personalize your CPMpyModel class if you want to.

## Useful links

Some useful documentation :
- The getting started CPMpy documentation : https://cpmpy.readthedocs.io/en/latest/modeling.html
- A quite complete tutorial on ORTools solver (expecially useful if you wish to optimize solver parameters or use ORTools logs): https://d-krupke.github.io/cpsat-primer/05_parameters.html

