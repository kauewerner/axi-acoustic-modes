# Axisymmetric Acoustic Modal Extraction

Compute the eigenvalues and eigenvectors of axisymmetric acoustic cavities using FEM (Finite Element Method). The mesh is created using [Gmsh](https://gmsh.info/) and the solution is carried out by [Nastran 95](https://github.com/nasa/NASTRAN-95)

Dependencies:
- [gmsh](https://gitlab.onelab.info/gmsh/gmsh/-/blob/master/api/gmsh.py) (Python API)
- [nastran](https://ubuntu.pkgs.org/16.04/ubuntu-multiverse-amd64/nastran_0.1.95-1_amd64.deb.html) (Ubuntu package) 
- numpy

In the [notes]() directory, one can find a pdf with all the information extracted from the Nastran manuals that is related to Acoustic simulation.

The next step is to extend the input cavity type to use custom axisymmetric profile shapes (under development...)
