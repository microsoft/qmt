FROM ubuntu:18.04
LABEL description="Microsoft QMT documentation build tool"

RUN adduser --disabled-password --gecos "" qmt_user

RUN apt update; \
    apt install -y --no-install-recommends \
        software-properties-common make \
        python3-sympy python3-scipy python3-shapely python3-dask python3-distributed \
        python3-sphinx pylint3 python3-toolz python3-h5py graphviz python3-pip; \
    python3 -m pip install m2r sphinx_rtd_theme

#RUN apt-add-repository -y ppa:freecad-maintainers/freecad-stable; \
#    apt update; \
#    apt install -y --no-install-recommends freecad; \
#    export PYTHONPATH=$PYTHONPATH:/usr/lib/freecad/lib

# NOTE: this ruffles the base_files package
RUN apt purge iso-codes libperl5.26; \
    apt autoremove; \
    apt clean

USER qmt_user
WORKDIR /qmt/doc
CMD python3 -m pip install --user -e ..; \
    sh configure.sh; \
    make html
