import signac

project = signac.init_project()

for crystal in ("bcc", "fcc"):
    for density in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        job = project.open_job({"crystal": crystal, "density": density}).init()
