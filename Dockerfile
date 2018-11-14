# To create your environment, run:
# docker build -t qmt:master .
# docker run -it qmt:master

FROM qmt_base

WORKDIR /app
COPY . /app/qmt
ENV PATH /usr/local/envs/py36/bin:$PATH
RUN cd qmt && python setup.py develop && cd ..
RUN cd qmt && /usr/local/envs/py27/bin/python setup.py develop && cd ..
