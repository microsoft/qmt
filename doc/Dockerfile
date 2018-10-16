FROM ubuntu:18.04
LABEL description="Microsoft QMT documentation build tool"

RUN adduser --disabled-password --gecos "" qmt_user

# Python 3 setup: this will be used in the future
#RUN apt update; \
#    apt install -y --no-install-recommends \
#        software-properties-common make \
#        python3-sympy python3-scipy python3-shapely python3-dask python3-distributed \
#        python3-sphinx pylint3 python3-toolz python3-h5py graphviz python3-pip; \
#    python3 -m pip install m2r sphinx_rtd_theme

# Python 2 setup: to build with FreeCAD functionality apidoc
RUN apt update; \
    apt install -y --no-install-recommends \
        software-properties-common make gcc \
        python-sympy python-scipy python-shapely \
        python-sphinx pylint python-h5py graphviz python-dev python-pip; \
    python -m pip install dask distributed toolz m2r sphinx_rtd_theme
#
RUN apt-add-repository -y ppa:freecad-maintainers/freecad-stable; \
    apt update; \
    apt install -y --no-install-recommends freecad; \
    echo 'import FreeCAD' > /usr/lib/python2.7/dist-packages/silly_fix.pth

# NOTE: this ruffles the base_files package
RUN apt purge iso-codes libperl5.26 python-dev gcc-7 python3-apt; \
    apt autoremove; \
    apt clean

USER qmt_user
WORKDIR /qmt/doc
ENV PYTHONPATH=$PYTHONPATH:/usr/lib/freecad/lib

#CMD python3 -m pip install --user -e ..;
#    sh configure.sh; \
#    make html
CMD python -m pip install --user -e ..; \
    sh configure.sh;\
    make html
