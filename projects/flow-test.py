# Copyright (c) 2017 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import logging
import os
import subprocess
import sys
from shutil import copytree
from tempfile import NamedTemporaryFile, TemporaryDirectory

from mistune import BlockLexer

logger = logging.getLogger()


def _find_descr(blocks):
    "The first paragraph is interpreted as the description."
    for block in blocks:
        if block["type"] == "paragraph":
            return block["text"]


def _find_test_code(blocks):
    "All code blocks within a 'using' or 'testing' section."
    found = False
    for block in blocks:
        if found and block["type"] == "code":
            yield block["text"]
        if block["type"] == "heading":
            found = block["text"].lower() in ("usage", "testing")


def _parse_readme(text):
    blocks = BlockLexer().parse(text)
    return {
        "description": _find_descr(blocks),
        "test_code": "\n".join(_find_test_code(blocks)),
    }


def _run_test(path, test_code, output, timeout):
    with TemporaryDirectory() as tmp:
        cwd = os.getcwd()
        try:
            logger.debug(f"Copy project into temporary directory '{tmp}'.")
            dst = copytree(path, os.path.join(tmp, "test"))
            os.chdir(dst)
            logger.debug("Start test.")
            for line in test_code:
                logger.info(" - " + line.strip())
                subprocess.check_call(
                    line,
                    shell=True,
                    timeout=timeout,
                    stderr=subprocess.STDOUT,
                    stdout=output,
                )
        except subprocess.CalledProcessError:
            raise RuntimeError(line, None)
        finally:
            os.chdir(cwd)


def run_tests(path, output, timeout):
    try:
        with open(os.path.join(path, "README.md")) as file:
            readme = _parse_readme(file.read())
    except FileNotFoundError:
        raise RuntimeWarning("README.md file missing.")
    else:
        logger.info("Executing code found in README.md file:")
        _run_test(path, readme["test_code"].split("\n"), output, timeout)
    try:
        with open(os.path.join(path, "test.sh")) as file:
            logger.info("Executing 'test.sh':")
            _run_test(path, list(file), output, timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeWarning("Test failed due to timeout.")
    except FileNotFoundError:
        logger.info("No test file!")


def main(args):
    logger.info(f"Testing '{args.path}'...")
    try:
        if args.output:
            run_tests(args.path, sys.stdout, args.timeout)
        else:
            with NamedTemporaryFile() as output:
                run_tests(args.path, output, args.timeout)
    except RuntimeError as error:
        logger.error("Error at line: {}".format(error.args[0]))
        raise RuntimeWarning("Test failed.")
    logger.info("OK")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="The path of the example project to test.")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase logging verbosity."
    )
    parser.add_argument("-l", "--log", help="Store log output in this file.")
    parser.add_argument(
        "-o",
        "--output",
        action="store_true",
        help="Print the testing output to screen.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=60,
        help="Specify a timeout in seconds after which a test automatically fails.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(name)s:%(levelname)s:%(message)s" if args.verbose else "%(message)s",
    )

    if args.log:
        fh = logging.FileHandler(args.log)
        fh.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s:%(levelname)s:%(message)s")
        )
        logger.addHandler(fh)

    try:
        main(args)
    except RuntimeWarning as w:
        print(w, file=sys.stderr)
        sys.exit(1)
