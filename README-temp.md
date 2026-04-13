# PMS Hackathon: guide for Tempo

Prerequisite: cmake is installed
1. Clone Tempo: `git clone https://gitlab.laas.fr/roc/emmanuel-hebrard/tempo.git`
2.create a build folder at the root of Tempo's repo and move into it (`cd tempo; mkdir build; cd build`)
3. run `cmake -DCMAKE_CXX_COMPILER=g++-11 -DCMAKE_BUILD_TYPE=release ..`
4. run `make boxes`

This will compile an executable whose code is in `src/examples/boxes.cpp`.

This is an empty model for the problem, with methods to read the instance files and returning a `vector<Box>` with `Box` a simple class holding the dimensions of the box. 

This program implements helpers to read the instances, print the solutions, and provides skeletons of:
1. A object (`BoxVariable`) grouping all the variables relative to a box 
2. A model (`BoxPackingModel`) with a method `BoxPackingModel::print_sol()` that prints a solution to std::out (for the visuzlization tool) and to a file (by default, the solution file). An example of usage via callback is provided. 
3. A user-defined heuristic (`MyHeuristic`)
4. A user-define LNS policy (`MyLNSPolicy`)

You can use this executable as basis for you solution.

Tempo's [Quickstart guide](#https://gitlab.laas.fr/roc/emmanuel-hebrard/tempo/-/edit/main/documentation/QUICKSTART.md?ref_type=heads) should be helpful.


