FROM ubuntu:18.04

#needs to be set since tzdate is a dependency
ENV DEBIAN_FRONTEND=noninteractive

# get the microsoft azure package source
RUN apt-get update && apt-get install -y wget
RUN wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb && dpkg -i packages-microsoft-prod.deb 

# install all elements
RUN apt-get update && apt-get install -y python3-notebook jupyter-core jupyter-notebook \
python3-pip python3-numpy python3-scipy python3-matplotlib blobfuse

RUN yes | pip3 install bokeh
RUN yes | pip3 install "holoviews[all]"

# since tzdate was installed noninteractively
RUN ln -fs /usr/share/zoneinfo/America/Vancouver /etc/localtime

RUN useradd -r -d /home/notebook -s /sbin/nologin -c "Docker image user" notebook


# Now mount the blob storage


# temporary directory for Blobfuse and user directories
RUN mkdir /mnt/blobfusetmp
RUN mkdir /home/notebook && mkdir /home/notebook/notebooks && mkdir /home/notebook/data
RUN chown notebook /mnt/blobfusetmp -R
RUN chown notebook /home/notebook -R

#set up working directory for the notebook
#RUN chmod -wx /home/notebook/data/


ADD access_keys.config /access_keys.config
RUN chown notebook /access_keys.config


ADD jupyter_notebook_config.py /jupyter_notebook_config.py
RUN chown notebook /jupyter_notebook_config.py


EXPOSE 8888

WORKDIR /home/notebook

USER notebook

ADD hall_data.ipynb /home/notebook/notebooks
ADD Vx1bxwaitq33_39.txt /home/notebook/Vx1bxwaitq33_39.txt


CMD ["jupyter", "notebook", "--config=/jupyter_notebook_config.py"]