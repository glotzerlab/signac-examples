import signac


def main():
    project = signac.init_project()
    for i in range(8):
        project.open_job({"i": i}).init()


if __name__ == "__main__":
    main()
