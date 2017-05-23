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

### Build the docker images
```bash
cd /into/this/repo
docker build -t tfserving .
```

### Run the docker image locally
```bash
docker run -d -p 8080:80 -p 9000:9000 --name serving tfserving
```

## Updating models
You can add a model in the `models_config.txt`. Just add a `config` key into the `model_config_list`. 
Model versions are stored in the `/tmp/models` base folder. Name the model (sub) folder the same as the model `name`.

```yaml
config: {
    name: "suicide",
    base_path: "/tmp/models/suicide",
    model_platform: "tensorflow"
}
```

## REST endpoints

### Uploading a model
Models are uploaded by querying the `/upload` endpoint with a `.zip` or `.tar.gz`. 
The file will get extracted and model checkpoints and graph definitions will be stored in `/tmp/models/model_name`. 
TensorFlow Serving will pick up the new model and reload it.
```bash
curl -X POST http://service.url/upload -H 'cache-control: no-cache' -H 'content-type: multipart/form-data' -F model_name=MODEL_NAME -F file=@FILE_LOCATION.{zip, tar.gz}
```

### Prediction
You can get a prediction by querying the `/prediction` endpoint. You need to specify and `"input"` and `"model_name`.
```bash
curl -X POST http://service.url/prediction -H 'cache-control: no-cache' -H 'content-type: application/json' -d '{"input": [[]], "model_name": "suicide"}'
```

## gRPC 

### Install gRPC for python
```bash
pip install grpcio
```

### Getting started with gRPC
TODO