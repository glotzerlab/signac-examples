"""Configuration of the project enviroment.

The environments defined in this module can be auto-detected.
This helps to define environment specific behaviour in heterogenous
environments.
"""
import flow
from flow.environment import format_timedelta


class RahmanEnvironment(flow.environment.TorqueEnvironment):
    hostname_pattern = 'master.cl.vanderbilt.edu'
    cores_per_node = 16

    @classmethod
    def script(cls, _id, nn, walltime, ppn=None, **kwargs):
        if ppn is None:
            ppn = cls.cores_per_node
        js = super(RahmanEnvironment, cls).script()
        js.writeline('#!/bin/sh -l')
        js.writeline('#PBS -j oe')
        js.writeline('#PBS -l nodes={}:ppn={}'.format(nn, ppn))
        js.writeline('#PBS -l walltime={}'.format(format_timedelta(walltime)))
        js.writeline('#PBS -q low')
        js.writeline('#PBS -N {}'.format(_id))
        js.writeline('#PBS -V')
        return js
