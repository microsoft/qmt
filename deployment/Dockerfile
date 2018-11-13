FROM ubuntu:16.04

#set up conda:
RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
       && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
       && bash /tmp/miniconda.sh -bfp /usr/local \
       && rm -rf /tmp/miniconda.sh \
       && conda install -y python=3 \
       && conda update conda \
       && apt-get -qq -y autoremove \
       && apt-get autoclean \
       && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
       && conda clean --all --yes
ENV PATH /opt/conda/bin:$PATH

# Copy the current directory contents into the container at /app
COPY environment_36.yml /install/
COPY environment_27.yml /install/
COPY dask_config.yaml /install/

# Run apt-gets:
RUN apt-get update && apt-get install -y \ 
       apt-utils \
       gcc \
       g++ \
       gfortran \
       hdf5-tools \
       make \
       git \
       cmake \
       libopenmpi-dev \
       software-properties-common \
       vim \
       apt-transport-https \
       gnupg2 \
       ca-certificates \
       slurm-client

# install freecad 0.16 and 0.17
RUN  apt-get update \
    && apt-add-repository -y ppa:freecad-maintainers/freecad-stable \
    && apt-get update \
    && apt-get install -y freecad 
RUN  apt-add-repository -y ppa:freecad-maintainers/freecad-legacy \
    && apt-get update \
    && apt-get install -y freecad-0.16 \
    && apt-get clean 

# set up python environments... this takes awhile:
RUN conda config --set always_yes yes --set changeps1 no
RUN conda update -q conda
RUN conda env create -v -q -n py36 -f /install/environment_36.yml
RUN conda env create -v -q -n py27 -f /install/environment_27.yml

# set the correct path for freeCAD and fix the link to limstdc++       
RUN echo "/usr/lib/freecad/lib">/usr/local/envs/py27/lib/python2.7/site-packages/freecad.pth \
       && rm /usr/local/envs/py27/lib/libstdc++.so.6 \
       && ln -s /usr/local/envs/py27/lib/libstdc++.so.6.0.24 /usr/local/envs/py27/lib/libstdc++.so.6
RUN rm /usr/local/envs/py36/lib/libstdc++.so.6 \
       && ln -s /usr/local/envs/py36/lib/libstdc++.so.6.0.24 /usr/local/envs/py36/lib/libstdc++.so.6

# clean up
RUN conda clean -pt

# clean up
RUN conda clean -pt

# move the dask config file into place
RUN mkdir /root/.dask && mv /install/dask_config.yaml /root/.dask/.

# Set the working directory to /app
WORKDIR /app
