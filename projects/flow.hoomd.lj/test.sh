python src/init.py 0
python src/project.py status -d -p 1
python src/project.py submit --pretend
python src/project.py run -o initialize --progress
python src/project.py run -o estimate --progress
python src/project.py run -o sample --progress
python src/project.py status -d
python -m jupyter nbconvert --to html --execute src/notebook.ipynb
