"""Configuration of custom environments.

The environments defined in this module can be auto-detected.
This helps to define environment specific behaviour in heterogenous
environments.
"""
import flow


class MyUniversityCluster(flow.DefaultTorqueEnvironment):

    hostname_pattern = 'mycluster.*.university.edu'
    cores_per_node = 32

    @classmethod
    def mpi_cmd(cls, cmd, np):
        return 'mpirun -np {np} {cmd}'.format(n=np, cmd=cmd)

    @classmethod
    def script(cls, _id, **kwargs):
        js = super(MyUniversityCluster, cls).script(_id=_id, **kwargs)
        js.writeline("$PBS -A {}".format(cls.get_config_value('account')))
        return js
