FROM ubuntu:18.04

# Install basic things
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install build-essential

# Set an user for app
RUN useradd -m calc_volume

WORKDIR /home/calc_volume

# Install library
RUN apt-get -y install libgdal-dev

# Install language
RUN apt-get -y install python3 python3-pip

ADD requirements.txt .

# GDAL package requires numpy, but it does not depend on it explicitly.
RUN pip3 install --trusted-host pypi.python.org numpy
RUN CPATH=/usr/include/gdal pip3 install --trusted-host pypi.python.org -r requirements.txt

ADD example example
ADD src src

CMD ["python3", "src/main.py", "example/sample00.tif", "POLYGON ((297854.531508583 4162781.09825457,297903.046025991 4162786.45581586,297904.401298411 4162773.53837561,297884.474558611 4162770.99723982,297884.813376716 4162767.6302349,297877.444082933 4162766.95259869,297877.041736433 4162770.29842748,297855.886781003 4162768.24434272,297854.531508583 4162781.09825457))"]
