FROM ubuntu:22.04

USER root
ENV DEBIAN_FRONTEND=noninteractive

# Update package list, upgrade system and set default locale
RUN apt-get update
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install apt-utils
RUN apt-get -y install locales
RUN locale-gen "en_US.UTF-8"
ENV LC_ALL "en_US.UTF-8"
ENV LANG "en_US.UTF-8"

# Install python3, and activate python3.10 as default python interpreter
RUN apt-get -y install python3-dev python3 python3-pip python3-venv
RUN pip3 install --upgrade pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install additional packages
RUN apt-get -y install ssh htop git vim net-tools curl build-essential sqlite3 psmisc

# install nodejs
RUN curl --insecure -sL https://deb.nodesource.com/setup_18.x -o /tmp/nodesource_setup.sh
RUN bash /tmp/nodesource_setup.sh
RUN apt-get -y install build-essential nodejs

# install npm packages globally
# RUN npm install next react react-dom -g

# Source the bashrc, used also with the services managed by supervisord.
RUN echo "source /shared/bashrc" >>/root/.bashrc

# Install python packages for data science
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN pip install --upgrade pip
RUN pip install wheel
ADD requirements0.txt /tmp/requirements0.txt
ADD requirements1.txt /tmp/requirements1.txt
ADD requirements2.txt /tmp/requirements2.txt
RUN bash -c "source root/.cargo/env && pip install -r /tmp/requirements0.txt"
RUN bash -c "source root/.cargo/env && pip install -r /tmp/requirements1.txt"
RUN bash -c "source root/.cargo/env && pip install -r /tmp/requirements2.txt"

# install http proxy
RUN apt-get -y install nginx apache2-utils
RUN rm -f /etc/nginx/nginx.conf && ln -s /shared/nginx.conf /etc/nginx/nginx.conf 

# Add Jupyter config
RUN mkdir -p /root/.jupyter
RUN ln -s /shared/jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py

# Enable Jupiter Voila extension
RUN jupyter serverextension enable voila
RUN jupyter server extension enable voila
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# Copy contents of shared folder
ADD . /shared

# Used to test if there's a mounted volume or not, showing a warning for data loss
RUN echo > /shared/warning_no_mounted_volume

# Add /shared to pythonpath: packages defined in this directory will be visible from Python.
ENV PYTHONPATH /shared/src/

# Change working directory
WORKDIR /shared

# Start supervisord, that takes care of running our services.
CMD ["supervisord" , "--nodaemon", "--configuration=/shared/supervisord.conf"]
# supervisord --nodaemon --configuration=/shared/supervisord.conf
#CMD ["/bin/bash"]

# Expose these TCP ports.
EXPOSE 8080/tcp
EXPOSE 8082/tcp
