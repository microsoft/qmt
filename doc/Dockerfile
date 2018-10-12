FROM ubuntu:18.04
LABEL description="Microsoft QMT documentation build tool"

RUN apt update; \
    apt install -y --no-install-recommends \
        make python3-sphinx pylint3 graphviz python3-pip; \
    python3 -m pip install m2r sphinx_rtd_theme

RUN adduser --disabled-password --gecos "" qmt_primary

USER qmt_primary
WORKDIR /qmt/doc
CMD python3 -m pip install --user -e ..; \
    sh configure.sh; \
    make html
