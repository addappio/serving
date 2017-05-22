import flask
import urllib
import tensorflow as tf
import cPickle as pickle
from waitress import serve
from grpc.beta import implementations
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

from google.protobuf.json_format import MessageToJson

app = flask.Flask(__name__)


@app.route('/prediction', methods=["GET", "POST"])
def model_prediction():
    host = "localhost"
    port = 9000

    url_input = flask.request.values.get('input')
    model_name = flask.request.values.get('model_name')

    model_input = pickle.loads(str(urllib.unquote(url_input)))

    channel = implementations.insecure_channel(host, int(port))
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    request = predict_pb2.PredictRequest()
    request.model_spec.name = model_name

    for k, v in model_input.items():
        request.inputs[k].CopyFrom(
            tf.contrib.util.make_tensor_proto(v))
    result = stub.Predict(request, 10.0)  # 10 secs timeout
    return MessageToJson(result)


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
