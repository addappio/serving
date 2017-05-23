import os
import json
import tarfile
import zipfile
from waitress import serve
from flask import Flask, request, jsonify, Response

UPLOAD_FOLDER = '/home/henriblancke/Downloads/models'
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


@app.route('/upload', methods=["POST"])
def upload_model():
    # check if the post request has the file part
    print request.form.get('model_name')
    if 'file' not in request.files:
        return response(status=400, response=dict(status="failed",
                                                  message="No file specified."))

    fn = request.files['file']

    if fn.filename == '':
        return response(status=400, response=dict(status="failed",
                                                  message="No file specified."))

    if fn and allowed_file(fn.filename):
        print "HERE"
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
    serve(app, host='0.0.0.0', port=3000)
