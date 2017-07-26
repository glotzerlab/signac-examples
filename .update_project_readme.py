#!/usr/bin/env python
import os
import sys
import glob
from mistune import BlockLexer


def _find_descr(blocks):
    "The first paragraph is interpreted as the description."
    for block in blocks:
        if block['type'] == 'paragraph':
            return block['text']


def generate_project_overview(file):
    file.write("## Project Overview\n\n")

    for fn in sorted(glob.glob('projects/*/README.md'), key=lambda fn: (fn.count('.'), fn)):
        dirname = os.path.dirname(fn)
        project_name = os.path.basename(dirname)
        file.write("### [{}]({}/)\n\n".format(project_name, dirname))
        with open(fn) as readme:
            files = BlockLexer().parse(readme.read())
            file.write(_find_descr(files) + '\n')
            file.write('\n    flow-clone https://bitbucket.org/glotzer/signac-examples.git#projects/{}\n\n'.format(project_name))


def parse_readme(readme):
    for i, line in enumerate(readme):
        if 'Project Overview' in line:
            yield i
        elif 'Copyright Notice' in line:
            yield i
            return


def generate_readme(readme, tmp):
    start, stop = parse_readme(readme)
    readme.seek(0)
    written = False
    for i, line in enumerate(readme):
        if i >= start and i < stop:
            if written:
                continue
            else:
                generate_project_overview(tmp)
                written = True
                continue
        else:
            tmp.write(line)


if __name__ == '__main__':
    fn_readme = 'projects/README.md'
    fn_readme_tmp = fn_readme + '.tmp'
    with open(fn_readme) as readme:
        with open(fn_readme_tmp, 'x') as tmp:
            generate_readme(readme, tmp)
    os.rename(fn_readme_tmp, fn_readme)
