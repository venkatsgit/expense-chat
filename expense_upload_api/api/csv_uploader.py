from flask import request, jsonify
from . import api_bp
import json
from process.csv_uploader import FileUploader


@api_bp.route('/csv/upload', methods=['POST'])
def upload_csv():
    user_id = "1"

    if 'file' not in request.files or 'file_name' not in request.form:
        return jsonify({'status': 'error', 'message': 'bad request'}), 400

    file_name = request.form['file_name']
    file = request.files['file']

    with open("file_meta_data_provider.json", "r") as json_file:
        file_meta_data_provider = json.load(json_file)
        if file_name not in file_meta_data_provider:
            return jsonify({'status': 'error', 'message': 'bad request'}), 400
        else:
            file_uploader = FileUploader(file,file_name,file_meta_data_provider[file_name],user_id)
            return file_uploader.validate_and_insert()
