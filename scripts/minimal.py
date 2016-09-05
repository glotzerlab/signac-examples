import signac
project = signac.init_project('MinimalExampleProject', 'minimal_example')
for p in 0.1, 1.0, 10.0:
    sp = {'p': p, 'kT': 1.0, 'N': 1000}
    with project.open_job(sp) as job:
        if 'V' not in job.document:
            V = sp['N'] * sp['kT'] / sp['p']
            job.document['V'] = V

for doc in project.index():
    print(doc)
