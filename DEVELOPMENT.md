# Development

These instructions have been tested on macOS Monterey @ MacBook Pro M2 with `Python 3.10.8`.

## Set up the OS

1. Install command line tools

```
xcode-select --install
```

2. Install pyenv/pyenv-virtualenv
```
brew update
brew install pyenv pyenv-virtualenv
```

3. Configure the shell, adding in `~/.zshrc`:
```
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
export PYENV_VIRTUALENV_DISABLE_PROMPT=1
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

4. List the installed Python versions:
```
pyenv versions
```

5. List the Python versions available for installation:
```
pyenv install --list
```

6. Install a specific Python version
```
pyenv install 3.10.7
```

7. (Optional) Set a global pyenv Python version
```
pyenv global 3.10.7
```

8. Install poetry
```
brew install poetry
poetry config virtualenvs.in-project true
```

9. Install jq

brew install jq


### (Optional) Optimizing the Zsh shell

The [powerlevel10k theme](https://github.com/romkatv/powerlevel10k) lets you customize the Zsh prompt,
showing the current folder, git status, and active environment. My `.zshrc`:

```
# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

source ~/bin/powerlevel10k/powerlevel10k.zsh-theme

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Required, to display the active environment on the prompt (right side)
plugins=(virtualenv)
```

Useful alises:
```
alias ll="/bin/ls -la"
alias ls="/bin/ls -laG"
```

## Manage the project environment

### Creating and removing the environment

To create it:

1. List the available Python versions:
```
pyenv versions
```

2. Create the environment (`./venv`):
```
cd stratosphere
poetry env use 3.10.7
```

3. Check the correct installation of the Poetry environment
```
poetry env info
```

4. To remove it:

```
cd stratosphere
rm -rf .venv
```

### Installing the project in development mode

1. Activate the environment
```
cd stratosphere
poetry shell
```

2. Install the project (edit mode) in the Poetry environment, including extras,
removing all packages that are not explicitly required by the package itself:

```
poetry install --all-extras --sync
```

3. Run the tests

```
poetry run pytest
```

### Useful Poetry commands to maintain the environment


Add a new package:
```
poetry add pandas
```

Add a new dev package:
```
poetry add --group dev jupyterlab
```

Update the lock file (to be done after changing packages):
```
poetry lock
```

List the available packages:
```
poetry show
```

Update packages to their latest compatible versions:
```
poetry update
```

Show the Poetry configuration:
```
poetry config --list
```

Show the path of the Poetry environment:
```
poetry env info -p
```

Check validity of pyproject.toml:
```
poetry check
```

Publish the package to PyPI, after buming the version (patch):

```
poetry version patch
poetry "-u$PYPI_USERNAME" "-p$PYPI_PASSWORD" --build publish
```


#### (Optional) Working with pyenv-virtualenv

We don't currently use pyenv-virtualenv, but keeping in case
we want to drop Poetry layer from the equation to debug issues
and test the installation on a clean environment.

##### Creating and environment

Create it:

```
pyenv virtualenv 3.8.10 test-stratosphere
pyenv activate test-stratosphere
pip install --upgrade pip
pip install wheel
```

Auto-activating the environment in a directory:

```
pyenv local test-stratosphere
```

##### Removing an environment

```
pyenv uninstall 3.8.10/envs/test-stratosphere
rm -rf ~/.pyenv/versions/3.8.10/envs/test-stratosphere
```

To unlink it from a project:

```
rm stratosphere37/.python-version
```

## Code quality

Combining
```
pytest
ruff src # https://github.com/charliermarsh/ruff
black .
```

* To ignore QA on a specific line, add `# noqa` at its end
* Things to take care of:

  * Boolean traps: https://adamj.eu/tech/2021/07/10/python-type-hints-how-to-avoid-the-boolean-trap/

## Running tests

Running a single test, without suppressing the output:

```
pytest -s tests/test_run.py::test_run_fields
```

Running coverage test:

```
pytest --cov=src/projectname tests/
```

Running coverate test, reporting missing lines:

```
pytest --cov=src/projectname --cov-report term-missing  tests/
```

To avoid .coverage files, you can add this line to your shell .rc:
(from https://github.com/pytest-dev/pytest-cov/issues/374)

```
export COVERAGE_FILE=/tmp/.coverage
```

Running pylint:

```
pylint src
```

## Building the package

```
poetry run utils/build_package.py
```

## Mkdocs

1. Create project: `mkdocs new .`
2. Preview with auto-reload: `mkdocs serve`

