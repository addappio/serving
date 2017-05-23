import os
import json
import tarfile
import zipfile
import tensorflow as tf
from waitress import serve
from grpc.beta import implementations
from flask import Flask, request, Response
from tensorflow_serving.apis import predict_pb2
from google.protobuf.json_format import MessageToJson
from tensorflow_serving.apis import prediction_service_pb2

# test
# curl -X POST http://localhost:8080/upload -H 'cache-control: no-cache' -H 'content-type: multipart/form-data'
# -F model_name=suicide -F file=@/home/henriblancke/Downloads/models/version1.zip

PORT = 9000
HOST = 'localhost'
UPLOAD_FOLDER = '/tmp/models'
ALLOWED_EXTENSIONS = {'zip', 'tar.gz', 'tar', 'gz'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def untar(fn, destination):
    filename = os.path.join(destination, fn.filename)
    fn.save(filename)
    fn.close()

    tar = tarfile.open(filename)
    tar.extractall(destination)
    tar.close()

    os.remove(filename)


def unzip(fn, destination):
    filename = os.path.join(destination, fn.filename)
    fn.save(filename)
    fn.close()

    zip = zipfile.ZipFile(filename)
    zip.extractall(destination)
    zip.close()

    os.remove(filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def response(response, status=200):
    return Response(status=status,
                    response=json.dumps(response),
                    mimetype='application/json')


@app.route('/', methods=["GET"])
def health():
    return response(status=200, response=dict(status="Ok",
                                              message="Stuff seems to be working well."))


@app.route('/prediction', methods=["GET", "POST"])
def get_prediction():
    if request.headers['Content-Type'] == 'application/json':

        payload = request.get_json()
        model_input = payload.get('input')
        model_name = payload.get('model_name')

        channel = implementations.insecure_channel(HOST, int(PORT))
        stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

        predict = predict_pb2.PredictRequest()
        predict.model_spec.name = model_name

        predict.inputs['inputs'].CopyFrom(tf.contrib.util.make_tensor_proto(model_input))

        result = stub.Predict(predict, 10.0)  # 10 secs timeout
        return Response(response=MessageToJson(result),
                        status=200,
                        mimetype='application/json')

    else:
        return response(status=400, response=dict(status="failed",
                                                  message="Content Type not accepted."))


@app.route('/upload', methods=["POST"])
def upload_model():
    # check if the post request has the file part
    if 'file' not in request.files:
        return response(status=400, response=dict(status="failed",
                                                  message="No file specified."))

    fn = request.files['file']

    if fn.filename == '':
        return response(status=400, response=dict(status="failed",
                                                  message="No file specified."))

    if fn and allowed_file(fn.filename):
        model_name = request.form.get('model_name')

        if not model_name:
            return response(status=400, response=dict(status="failed",
                                                      message="No model name specified."))

        destination = os.path.join(app.config['UPLOAD_FOLDER'], model_name)

        error_message = response(status=417, response=dict(status="failed",
                                                           message="Error when decompressing file."))

        if fn.filename.endswith("zip"):
            try:
                unzip(fn, destination)
            except Exception as _:
                print _
                return error_message

        if fn.filename.endswith('tar.gz'):
            try:
                untar(fn, destination)
            except Exception as _:
                print _
                return error_message

        return response(status=200, response=dict(status="success",
                                                  message="File uploaded and decompressed."))

    else:
        return response(status=415, response=dict(status="failed",
                                                  message="Media type not allowed."))


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
