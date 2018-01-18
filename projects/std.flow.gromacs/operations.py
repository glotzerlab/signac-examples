import project as flow_project

gmx_exec = "gmx_mpi" # Assumes mpi build

def ionize(job):
    """Exploit the pexpect module to run.
    Somewhat messy currently to use the project level data, but I don't have a better version for now"""
    import pexpect
    with job:
        cmd='{gmx} genion -s {io_config} -o {ionized_gro} -p -pname {pname} -nname {nname} -neutral'.format(
                gmx=gmx_exec,
                io_config=flow_project.ionization_config, ionized_gro=flow_project.ionized_file,
                pname=flow_project.pname, nname=flow_project.nname)
        child = pexpect.spawn(cmd)
        child.expect('Select a group:*')
        child.send('13\n')
        print(child.before.decode('ascii'))
        print(child.after.decode('ascii'))
        child.expect(pexpect.EOF)
        print(child.before.decode('ascii'))

if __name__ == '__main__':
    import flow
    flow.run()
