import pexpect  # Used to automate interaction with GROMCAS interface.

from project import pname, nname, ionization_config, ionized_file, gmx_exec


def ionize(job):
    """Exploit the pexpect module to run."""
    with job:
        cmd = "{gmx} genion -s {io_config} -o {ionized_gro} " \
            "-p -pname {pname} -nname {nname} -neutral".format(
                gmx=gmx_exec,
                io_config=ionization_config, ionized_gro=ionized_file,
                pname=pname, nname=nname)
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
