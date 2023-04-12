import os
import sys

from fabric import task

# make sure that we import the package from this directory
sys.path = ["."] + sys.path

# Initialise project directory and name
project_dir = os.path.abspath(os.path.dirname(__file__))
project_name = os.path.basename(project_dir)

# Change directory to directory containing this script
os.chdir(project_dir)


@task
def kill(ctx):
    with ctx.cd(project_dir):
        local(ctx, f"docker stop {project_name} 2>/dev/null >/dev/null || true")


@task
def dump(ctx):
    kill(ctx)
    local(ctx, f"docker save -o {project_name}.docker-image {project_name}")


@task
def start(ctx):
    kill(ctx)
    with ctx.cd(project_dir):
        local(
            ctx,
            f"docker run --rm --name {project_name} -d -ti -p 127.0.0.1:80:80 -p 127.0.0.1:8080:8080 -p"
            f" 127.0.0.1:8081:8081 -p 127.0.0.1:1080:1080 -p 127.0.0.1:8000:8000 -v {project_dir}/:/shared -t"
            f" {project_name}".format(project_dir=project_dir),
        )

    print("\n\nIndex of services: http://127.0.0.1:80/api/static/index.html\n\n")


@task
def start2(ctx):
    kill(ctx)
    with ctx.cd(project_dir):
        local(
            ctx,
            f"docker run --rm --name {project_name} -d -ti -p 127.0.0.1:80:80 -t {project_name}".format(
                project_dir=project_dir
            ),
        )
    print("\n\nIndex of services: http://127.0.0.1:80/api/static/index.html\n\n")


@task
def build(ctx):
    with ctx.cd(project_dir):
        local(ctx, f"docker build -t {project_name} .")


def local(ctx, *args, **kwargs):
    print("Executing: {} {}".format(args, kwargs))
    return ctx.run(*args, **kwargs)


def docker_exec(ctx, cmdline):
    with ctx.cd(project_dir):
        local(ctx, f"docker exec -ti {project_name} {cmdline}", pty=True)


@task
def shell(ctx):
    docker_exec(ctx, "/bin/bash")
