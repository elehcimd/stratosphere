import glob
import os
import subprocess

project_dir = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir)
project_name = os.path.basename(project_dir)


def local(args):
    cmd = " ".join(args) if type(args) == list else args
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode("utf-8")


def check_usage(py_files):
    md_files = glob.glob("mkdocs/**/*.md", recursive=True)
    md_text = "".join([open(md_file).read() for md_file in md_files])
    for py_file in py_files:
        if py_file not in md_text:
            print(f"Warning: {py_file} not linked")


def main():
    os.chdir(project_dir)

    rm_files = glob.glob("mkdocs/**/*.out", recursive=True) + glob.glob("mkdocs/**/*.src", recursive=True)
    for idx, rm_file in enumerate(rm_files):
        print(f"[{idx+1}/{len(rm_files)}] Removing {rm_file}")
        os.remove(rm_file)

    py_files = glob.glob("mkdocs/**/*.py", recursive=True)
    py_files = [py_file for py_file in py_files if py_file != "mkdocs/mymacros.py"]

    check_usage(py_files)

    for idx, py_file in enumerate(py_files):
        print(f"[{idx+1}/{len(py_files)}] Executing {py_file}")
        out = local(f"python {py_file}")
        with open(f"{py_file}.out", "w") as f:
            f.write(out)

        out = local(f'sh -c "cat {py_file} | black --line-length 75 -q -"')
        with open(f"{py_file}.src", "w") as f:
            f.write(out)

    local("touch mkdocs.yml")

    print("Operation completed.")


if __name__ == "__main__":
    main()
