import os

from common import get_package_version, project_dir, project_name

project_dir = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir)
project_name = os.path.basename(project_dir)


def execute(cmd):
    print(f"Executing: {cmd}")
    assert os.system(cmd) == 0


def inc_version():
    execute("poetry version patch")

    pkg_version = get_package_version(f"{project_dir}/pyproject.toml")

    with open(f"{project_dir}/src/{project_name}/version.py", "w") as f:
        f.write(f'__version__ = "{pkg_version}"\n')

    return pkg_version


def pytest():
    execute("poetry run pytest")


def main():
    os.chdir(project_dir)
    pytest()
    pkg_version = inc_version()
    execute("poetry run python utils/build_badges.py")
    execute("poetry build")

    # execute("ls -la dist/")
    print(f"Package {project_name} v{pkg_version} ready!")
    print('To publish:\n 1. $ poetry "-u$PYPI_USERNAME" "-p$PYPI_PASSWORD" --build publish\n 2. update repository')


if __name__ == "__main__":
    main()
