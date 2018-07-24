FROM ubuntu:18.04

#needs to be set since tzdata is a dependency
ENV DEBIAN_FRONTEND=noninteractive

# install all elements
RUN apt-get update && apt-get install -y python3-notebook jupyter-core jupyter-notebook \
	python3-pip python3-numpy python3-scipy python3-matplotlib

RUN yes | pip3 install bokeh
RUN yes | pip3 install "holoviews[all]"

# temporary directory for Blobfuse and user directories
RUN mkdir /notebook && mkdir /notebook/notebooks && mkdir /notebook/notebook_templates \
	&& mkdir /notebook/data

RUN useradd -r -d /notebook -s /sbin/nologin -c "notebook user" notebook


ADD jupyter_notebook_config.py /jupyter_notebook_config.py
RUN chown notebook /notebook -R && chown notebook /jupyter_notebook_config.py

RUN chmod 777 /notebook -R && chmod 777 /notebook/data /notebook/notebook_templates -R

EXPOSE 8888

# Add Tini. Tini operates as a process subreaper for jupyter. This prevents
# kernel crashes.
ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]



WORKDIR /notebook

USER notebook

ADD hall_data.ipynb /notebook/notebook_templates
ADD Vx1bxwaitq33_39.txt /notebook/data/Vx1bxwaitq33_39.txt


CMD ["jupyter", "notebook", "-y", "--config=/jupyter_notebook_config.py"]