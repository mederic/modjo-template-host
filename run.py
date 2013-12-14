import dataset
import json
from flask import Flask
from flask import send_from_directory
from flask import request
from core.template import *
import os

app = Flask(__name__)
app.config.from_object('config.BaseConfiguration')

TEMPLATE_TABLE = 'template'

@app.route('/template', methods=['GET'])
def template_list():
    return "List"

@app.route('/template', methods=['POST'])
def add_template():
    can_upload = app.config['ANYONE_CAN_UPLOAD']
    if not can_upload:
        candidate = request.form.get('secret')
        can_upload = candidate == app.config['ADMIN_SECRET']

    if can_upload:
        f = request.files.get('data')
        if f:
            # Template creation/validation
            template = Template()
            try:
                template.init_with_zip(f)
            except:
                return error(11, 'invalid template')
            if not template.check_valid_id():
                return error(12, 'invalid template id')

            # Template insertion in database
            db = dataset.connect(app.config['DATABASE_URI'])
            tpl_table = db[TEMPLATE_TABLE]
            if not tpl_table.find_one(tpl_id=template.id) is None:
                return error(13, 'template id already exists...')
            else:
                tpl_table.insert(template.to_dict())

            # Template storage
            template_folder = app.config['TEMPLATE_FOLDER']
            if not os.path.exists(template_folder):
                os.makedirs(template_folder)

            f.save(os.path.join(template_folder, template.id))
            return success('template added', {'tpl_id': template.id, 'edit_hash': template.edit_hash})
        else:
            return error(10, 'missing template')
    else:
        return error(2, 'access denied')

@app.route('/template/<tpl_id>', methods=['GET'])
def template_details(tpl_id):
    return "details"

@app.route('/template/<tpl_id>', methods=['POST'])
def upload_template_package(tpl_id):
    return "upload"

@app.route('/template/<tpl_id>.zip', methods=['GET'])
def download_template_package(tpl_id):
    db = dataset.connect(app.config['DATABASE_URI'])
    tpl_table = db[TEMPLATE_TABLE]
    if tpl_table.find_one(tpl_id=tpl_id) is None:
        return error(20, 'unexisted template.')

    template_folder = app.config['TEMPLATE_FOLDER']
    zip_path = os.path.join(template_folder, tpl_id)
    if not os.path.exists(zip_path):
        return error(21, 'corrupted server.')

    return send_from_directory(template_folder, tpl_id, as_attachment=True)


def error(code, msg):
    return json.dumps({'success': False, 'code': code, 'error': msg})

def success(msg, extra_data):
    result = {'success': True}
    if not extra_data is None:
        result['data'] = extra_data

    return json.dumps(result)

if __name__ == "__main__":
    app.run()