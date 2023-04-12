import json
import os

import anybadge
from common import local, pkg_version, project_dir, project_name


def tests_coverage():
    pytest_output = local("pytest --cov=src/mltraq tests/")

    pos_end = pytest_output.find(" passed")
    pos = pos_end
    while pos > 1 and pytest_output[pos - 1] != "=":
        pos -= 1
    n_passed_tests = int(pytest_output[pos:pos_end])

    percent_covered = float(local("coverage json -o /dev/stdout --quiet | jq .totals.percent_covered"))

    # Also, save it to file, linked to SVG image
    local("coverage report > coverage.txt")

    percent_covered = int(percent_covered)

    return n_passed_tests, percent_covered


def get_pkg_version_latest_pypi():
    """Returns the pypi latest version. Not used since it ends up being always outdated.

    Returns:
        _type_: _description_
    """
    pip_output = local(f"pip index versions {project_name}")
    return pip_output[pip_output.find("LATEST:") + 7 :].strip()


def main():
    os.chdir(project_dir)

    print("Updating badges ...")

    n_passed_tests, percent_covered = tests_coverage()

    stats = {}
    stats["test"] = f"passing ({n_passed_tests})"
    stats["coverage"] = f"{percent_covered}%"
    stats["pypi"] = pkg_version  # get_pkg_version_latest_pypi()
    stats["license"] = "BSD-3"
    stats["code-style"] = "black"
    stats["python"] = ">=3.8"

    coverage_thresholds = {0.6: "red", 0.7: "orange", 0.9: "yellow", 1: "green"}

    anybadge.Badge("test", stats["test"]).write_badge("mkdocs/assets/img/badges/test.svg", overwrite=True)
    anybadge.Badge("coverage", stats["coverage"], thresholds=coverage_thresholds).write_badge(
        "mkdocs/assets/img/badges/coverage.svg", overwrite=True
    )
    anybadge.Badge("pypi", stats["pypi"]).write_badge("mkdocs/assets/img/badges/pypi.svg", overwrite=True)
    anybadge.Badge("license", stats["license"], default_color="gray").write_badge(
        "mkdocs/assets/img/badges/license.svg", overwrite=True
    )
    anybadge.Badge("code style", stats["code-style"], default_color="black").write_badge(
        "mkdocs/assets/img/badges/code-style.svg", overwrite=True
    )
    anybadge.Badge("python", stats["python"]).write_badge("mkdocs/assets/img/badges/python.svg", overwrite=True)

    print(json.dumps(stats, indent=4))


if __name__ == "__main__":
    main()
