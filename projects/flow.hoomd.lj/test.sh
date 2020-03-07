python src/init.py 0
python src/project.py status -d -p 1
python src/project.py submit --test
python src/operations.py initialize --np 1 --progress
python src/project.py run --np 1 --progress   # estimate/sample
python src/project.py run --np 1 --progress   # estimate/sample
python src/project.py status -d
python -m jupyter nbconvert --to html --execute src/notebook.ipynb
