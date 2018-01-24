import os
import signac
import subprocess

# Make sure to update the path to your Quantum Espresso installation!
PWX = '/usr/bin/pw.x'


def create_infile(job, method, ecut):
    project = signac.get_project()
    with open(project.fn('vc-relax.in')) as template:
        with open(job.fn('{}.in'.format(method)), 'w') as infile:
            infile.write(template.read().format(
                prefix='calc',
                wfcdir=job.fn('wcf'),
                lattice_parameter=job.sp.lattice_parameter,
                number_of_bands=job.sp.number_of_bands,
                outdir=job.fn('out'),
                pseudo_dir=os.path.join(project.root_directory(), 'pseudo'),
                method=method,
                potential=job.sp.potential,
                ecut=ecut))
    return infile.name


def vc_relax(job):
    converged = False
    for e_cut in [160, 40, 60, 80, 100, 150, 200, 250, 300, 400, 500]:
        print('Attempting ecut={}'.format(e_cut))
        infile = create_infile(job, 'vc-relax', e_cut)
        cmd = '{} < {} > {}'.format(PWX, infile, job.fn('vc-relax.out'))
        subprocess.check_call(cmd, shell=True)
        with open(job.fn('vc-relax.out')) as outfile:
            for line in outfile:
                if(line.startwith('!')):
                    converged = True
                    break
        if(converged):
            job.document['ecut'] = e_cut
            break
    else:
        raise RuntimeError('Did not converge for ecut values!')


def scf(job):
    infile = create_infile(job, 'scf', job.document['ecut'])
    print(job.fn('scf.out'))
    subprocess.check_call(
        '{} < {} > {}'.format(PWX, infile, job.fn('scf.out')), shell=True)


if __name__ == "__main__":
    import flow
    flow.run()
