# About

This is a hello world example flow project.
It features a *hello* operation, which prints `Hello {job._id}` to screen and writes the same string to a file.

## Usage

```
signac job --create '{"a": 42}'
python project.py run
python project.py status --detailed
```
