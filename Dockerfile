FROM ubuntu:18.04

# Install basic things
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install build-essential
RUN apt-get -y install python3 python3-pip

# Install requirements
RUN apt-get -y install libgdal-dev

# Set an user for app
RUN useradd -m calc_volume

WORKDIR /home/calc_volume

ADD requirements.txt .
# GDAL package requires numpy, but it does not depend on it explicitly.
RUN pip3 install --trusted-host pypi.python.org numpy
RUN CPATH=/usr/include/gdal pip3 install --trusted-host pypi.python.org -r requirements.txt

ADD example example
ADD src src

CMD ["python3", "src/main.py"]
