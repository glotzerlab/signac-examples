import signac

def main():
    project = signac.init_project("AggregationMPI")
    for i in range(20):
        project.open_job({"i": i}).init()

if __name__ == "__main__":
    main()
