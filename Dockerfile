FROM ubuntu:16.04

MAINTAINER Henri Blancke

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
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

# Set up gRPC
RUN pip install \
        enum34 \
        futures \
        mock \
        six \
        flask \
        scipy \
        scikit-learn \
        requests \
        waitress \
        tensorflow \
        && \
    pip install --pre 'protobuf>=3.0.0a3' && \
    pip install -i https://testpypi.python.org/simple --pre grpcio

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
WORKDIR /

RUN update-ca-certificates -f

RUN mkdir /bazel && \
    cd /bazel && \
    curl -fSsL -O https://github.com/bazelbuild/bazel/releases/download/0.4.5/bazel-0.4.5-installer-linux-x86_64.sh && \
    chmod +x bazel-*.sh && \
    ./bazel-0.4.5-installer-linux-x86_64.sh && \
    cd / && \
    rm -f /bazel/bazel-0.4.5-installer-linux-x86_64.sh

RUN mkdir /serving && \
    mkdir -p /root && \
    mkdir -p /tmp/models

COPY tools /serving/tools
COPY setup.sh /root/setup.sh
COPY tf_models /serving/tf_models
COPY WORKSPACE /serving/WORKSPACE
COPY tensorflow /serving/tensorflow
COPY tensorflow_serving /serving/tensorflow_serving

RUN cd /serving/tensorflow && \
    yes "" | ./configure

RUN cd /serving/ && \
    bazel build -c opt --local_resources 2048,.5,1.0 tensorflow_serving/...

EXPOSE 9000 8080
CMD /root/setup.sh