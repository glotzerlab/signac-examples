import mbuild as mb
from mbuild.examples import Alkane

from util.decorators import job_chdir


@job_chdir
def initialize(job):
    "Inialize the simulation"
    alkane = Alkane(job.statepoint()['C_n'])
    n_alkane = 200
    # A cleaner packing approach would involve pull #372
    system_box = mb.Box([4, 4, 4])
    system = mb.fill_box(compound=alkane,
                         n_compounds=n_alkane,
                         box=system_box)
    system.save('init.gro',
                overwrite=True)
    system.save('init.top',
                forcefield_name='oplsaa',
                overwrite=True)


if __name__ == '__main__':
    import flow
    flow.run()
