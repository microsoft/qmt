FROM ubuntu:16.04

# Set up conda:
RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    && conda update -q conda \
    && ln -s /usr/local/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && . /usr/local/etc/profile.d/conda.sh \
    && conda activate \
    && conda clean -aq \
    && apt-get -qq -y autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log

# Run apt-gets:
RUN apt-get update && apt-get install -y \ 
    gcc \
    vim \
    libgl1-mesa-glx \
    slurm-client

# Set the working directory to /app
WORKDIR /app

# Copy QMS into the container and set up
# TODO: Only copy code and not deployment/doc/examples
COPY . qmt/

# Set up python environments... this takes awhile:
RUN conda config --set always_yes yes --set changeps1 no \
    && conda env create -v -q -n py36 -f qmt/environment.yml \
    && conda clean -aq \
    && conda activate py36

# Set the correct path for freeCAD   
RUN find /usr/local/pkgs/ -maxdepth 1 -type d -name freecad* | tail -n 1 | awk '{print $1"/lib"}' \
    > /usr/local/envs/py36/lib/python3.6/site-packages/freecad.pth

# Move the dask config file into place
RUN mkdir /root/.dask && mv qmt/deployment/dask_config.yaml /root/.dask/.

# Install QMT
RUN conda install -yq conda-build && conda develop -n py36 /qmt
