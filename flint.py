
from sys import argv as cmd_args
from os.path import exists as ignore_exists

from tools import (
    lint_file, 
    evaluate_lint_type,
    do_lint
)

# usage:
## python.exe flint.py <-f, -d, -md> "<input(file, directory)>" "<output directory>"
## ex.
### python flint.py -f "some_dir/myFile.txt" "myProjectPath"
##

def main():
    lintType = evaluate_lint_type(cmd_args[1:])
    projectPath = cmd_args[2:][0]
    projectDir = projectPath.split('/')[-1]

    if not ignore_exists(f"{projectPath}/.flint-ignore"):
        print(" !-! please add a '.flint-ignore' to your project !-!\n")
        return

    lintIgnore = []
    with open(f"{projectPath}/.flint-ignore", 'r') as fd:
        lines = fd.readlines()
        for line in lines:
            lintIgnore.append(f"{projectDir}/{line.rstrip()}")

    do_lint(lintType, cmd_args[2:], lintIgnore)

if __name__ == "__main__":
    main()
