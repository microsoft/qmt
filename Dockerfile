FROM ubuntu:18.04

# Install packages
RUN apt-get -qq update && \
    apt-get install -qq -y \
    apt-transport-https \
    apt-utils \
    bzip2 \
    ca-certificates \
    cmake \
    curl \
    gcc \
    gfortran \
    git \
    gnupg2 \
    g++ \
    hdf5-tools \
    libgl1-mesa-glx \
    libopenmpi-dev \
    libopenblas-dev \
    make \
    slurm-client \
    software-properties-common \
    sudo \
    vim \
    wget && \
    apt-get -qq -y autoremove && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/* /var/log/dpkg.log 

# Set up conda:
ENV PATH /usr/local/bin:$PATH
RUN curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -bfp /usr/local && \
    rm -rf /tmp/miniconda.sh && \
    conda update -q conda && \
    conda clean -aq && \
    ln -s /usr/local/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /usr/local/etc/profile.d/conda.sh" >> ~/.bashrc
# Set the working directory to /app
WORKDIR /app

# Copy QMT into the container and set up
# TODO: Only copy code and not deployment/doc/examples
COPY . qmt/

# Set up python environment... this takes awhile:
RUN conda config --set always_yes yes --set changeps1 no && \
    conda env create -v -q -f qmt/deployment/environment_full_linux.yml && \
    conda clean -aq && \
    echo "conda activate py36" >> ~/.bashrc
ENV PATH /usr/local/envs/py36/bin:$PATH

# Expose 8888 for jupyter notebook
EXPOSE 8888

# Set the correct path for freeCAD
# and fix the link to libstdc++, which is currently a conda bug
RUN find /usr/local/pkgs/ -maxdepth 1 -type d -name freecad* | \
    tail -n 1 | awk '{print $1"/lib"}' > \
    /usr/local/envs/py36/lib/python3.6/site-packages/freecad.pth

# Move the dask config file into place
RUN mkdir /root/.dask && mv qmt/deployment/dask_config.yaml /root/.dask/.

# Install QMT
RUN cd qmt && python setup.py develop
