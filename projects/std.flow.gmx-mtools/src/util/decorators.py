import os


def job_chdir(func):
    def func_wrapper(job, *args):
        cwd = os.getcwd()
        os.chdir(job.workspace())
        func(job, *args)
        os.chdir(cwd)
    return func_wrapper
