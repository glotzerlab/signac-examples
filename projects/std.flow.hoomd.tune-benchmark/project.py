from flow import FlowProject
from flow import staticlabel
# import flow.environments  # uncomment to use default environments


class Project(FlowProject):

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)

    @staticlabel()
    def tuned(job):
        return 'integrator' in job.document

    @staticmethod
    def _mean_per_np(job, measure):
        x = job.document[measure]
        return {int(np): sum(x[np])/len(x[np]) / int(np) for np in x}

    @classmethod
    def best_np(cls, job):
        mps = cls._mean_per_np(job, 'MPS')
        for np in sorted(mps, key=lambda np: 1.0 / mps[np]):
            return np

    def classify(self, job):
        yield from super().classify(job)

        if 'MPS' in job.document:
            mps = self._mean_per_np(job, 'MPS')
            yield 'MPS/np:' + '|'.join(('{}={:.1e}'.format(np, mps[np]) for np in sorted(mps)))

        if 'TPS' in job.document:
            mps = self._mean_per_np(job, 'TPS')
            yield 'TPS/np:' + '|'.join(('{}={:.1e}'.format(np, mps[np]) for np in sorted(mps)))

        try:
            yield 'NP-rec:{}'.format(self.best_np(job))
        except KeyError:
            pass


if __name__ == '__main__':
    Project().main()
