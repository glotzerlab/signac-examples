Template for MoSDeF- and GROMACS-centric project managed with signac

See [generic signac template](https://github.com/glotzerlab/signac-project-template) and [a fork](https://github.com/summeraz/monolayer_screening)

# Installation

Install these packages:

* [block_avg](https://github.com/tcmoore3/block_avg)
* [mtools](https://github.com/mattwthompson/mtools)

Install other dependencies:

```
python setup.py install
```


# Get started:

Initialize project:

```
python src/init.py
```

Build systems and perform energy minimization:

```
python src/project.py run initialize
python src/project.py run em  # energy minimization
```

Submit equilibration and production runs to the cluster
(can also be run locally as above)

```
python src/project.py submit -o equil
python src/project.py submit -o sample
```

At any time you can evaluate the status of each job with:

```
python src/project.py status -d
```

Analyze system (here, simple timeseries plots of density)

```
python analysis/calc_density.py
```

Look at the PDF file located in the `workspace` directory. It should look something like this:

![image](https://user-images.githubusercontent.com/7935382/28077533-a8a43f84-6627-11e7-9370-1206160d185d.png)
