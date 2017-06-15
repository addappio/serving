FROM ubuntu:16.04

MAINTAINER Addapp Corp.

WORKDIR /

RUN mkdir /serving && \
    mkdir -p /root && \
    mkdir -p /tmp/models

COPY http /serving/http
COPY models/ /tmp/models/
COPY tools /serving/tools
COPY setup.sh /root/setup.sh
COPY WORKSPACE /serving/WORKSPACE
COPY tensorflow /serving/tensorflow
COPY requirements.txt /root/requirements.txt
COPY tensorflow_serving /serving/tensorflow_serving
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        curl \
        git \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python-dev \
        python-numpy \
        python-pip \
        software-properties-common \
        swig \
        zip \
        zlib1g-dev \
        libcurl3-dev \
        vim \
        supervisor \
        openssh-server \
        nginx \
        libpq-dev \
        rsyslog \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pip
RUN curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Install requirements
RUN pip install -r /root/requirements.txt
RUN pip install -r /serving/http/requirements.txt

# Set up Bazel & JDK8
RUN add-apt-repository -y ppa:openjdk-r/ppa && \
    apt-get update && \
    apt-get install -y openjdk-8-jdk openjdk-8-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Running bazel inside a `docker build` command causes trouble, cf: https://github.com/bazelbuild/bazel/issues/134
# The easiest solution is to set up a bazelrc file forcing --batch.
RUN echo "startup --batch" >>/root/.bazelrc

# Similarly, we need to workaround sandboxing issues: https://github.com/bazelbuild/bazel/issues/418
RUN echo "build --spawn_strategy=standalone --genrule_strategy=standalone" \
    >>/root/.bazelrc
ENV BAZELRC /root/.bazelrc

# Install the most recent bazel release.
RUN update-ca-certificates -f

RUN mkdir /bazel && \
    cd /bazel && \
    curl -fSsL -O https://github.com/bazelbuild/bazel/releases/download/0.4.5/bazel-0.4.5-installer-linux-x86_64.sh && \
    chmod +x bazel-*.sh && \
    ./bazel-0.4.5-installer-linux-x86_64.sh && \
    cd / && \
    rm -f /bazel/bazel-0.4.5-installer-linux-x86_64.sh

RUN cd /serving/tensorflow && \
    yes "" | ./configure

RUN cd /serving/ && \
    bazel build -c opt --local_resources 4096,2.0,1.0 tensorflow_serving/model_servers:tensorflow_model_server

# Make NGINX run on the foreground
RUN echo "daemon off;" >> /etc/nginx/nginx.conf && \
    rm /etc/nginx/sites-enabled/default
# Copy the modified nginx conf
COPY nginx.conf /etc/nginx/conf.d/

EXPOSE 9000 80
CMD ["/usr/bin/supervisord", "-c",  "/etc/supervisor/conf.d/supervisord.conf"]