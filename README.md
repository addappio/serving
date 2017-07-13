# TensorFlow Serving

>TensorFlow Serving is an open-source software library for serving
machine learning models. It deals with the *inference* aspect of machine
learning, taking models after *training* and managing their lifetimes, providing
clients with versioned access via a high-performance, reference-counted lookup
table.

## Tutorials

* [Basic tutorial](tensorflow_serving/g3doc/serving_basic.md)
* [Advanced tutorial](tensorflow_serving/g3doc/serving_advanced.md)

## For more information

* [Serving architecture overview](tensorflow_serving/g3doc/architecture_overview.md)
* [TensorFlow website](http://tensorflow.org)

## Getting started

### Clone this bad boy
```bash
git clone --recurse-submodules https://github.com/addappio/serving
```

### Build the docker images
```bash
cd /into/this/repo
docker build -t tfserving .
```

### Run the docker image locally
```bash
docker run -d -p 8080:80 -p 9000:9000 --name serving tfserving
```

## Adding additional models
You can add a model in the `/models/models_config.txt`. Just add a `config` key into the `model_config_list`. 
Model versions are stored in the `/tmp/models` base folder. Name the model (sub) folder the same as the model `name`.

```yaml
config: {
    name: "MODEL_NAME",
    base_path: "/tmp/models/MODEL_NAME",
    model_platform: "tensorflow"
}
```

## gRPC 

### Install gRPC for python
```bash
pip install grpcio
```
