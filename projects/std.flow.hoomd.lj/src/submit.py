import flow
from project import MyProject

project = MyProject()
env = flow.get_environment(test=True)

# Operate all ops separately
for job in project:
    for op in project.next_operations(job):
        js = env.script(_id='{}-{}'.format(job, op), num_nodes=op.np)
        js.writeline(op.cmd)
        env.submit(js)
