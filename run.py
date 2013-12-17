import dataset
import json
from flask import Flask
from flask import send_from_directory
from flask import request
from flask import render_template
from flask import abort
from core.template import *
import os

app = Flask(__name__)
app.config.from_object('config.BaseConfiguration')

TEMPLATE_TABLE = 'template'

@app.route('/')
def index():
    templates = get_all_templates()
    return render_template('index.html', templates=templates, page='index')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    error = False
    success = False
    if request.method == 'POST':
        result = do_add_template(True, request.files)
        success = result
        error = not result
        
    return render_template('upload.html', page='upload', success=success, error=error)
    
@app.route('/template', methods=['GET'])
def template_list():    
    result = get_all_templates()
    return success('template list', result)
    

def get_all_templates():
    db = dataset.connect(app.config['DATABASE_URI'])
    tpl_table = db[TEMPLATE_TABLE]
    result = []
    for tpl_row in tpl_table.all():
        result.append(tpl_row_to_dict(tpl_row))
    return result

@app.route('/template', methods=['POST'])
def add_template():
    do_add_template(False, request.files)
    
def do_add_template(must_return_bool, request_files):
    can_upload = app.config['ANYONE_CAN_UPLOAD']
    if not can_upload:
        candidate = request.form.get('secret')
        can_upload = candidate == app.config['ADMIN_SECRET']

    if can_upload:
        f = request_files.get('data')
        if f:
            # Template creation/validation
            template = Template()
            try:
                template.init_with_zip(f)
            except:
                if must_return_bool:
                    return False
                else:
                    return error(11, 'invalid template')
            if not template.check_valid_id():
                if must_return_bool:
                    return False
                else:
                    return error(12, 'invalid template id')

            # Template insertion in database
            db = dataset.connect(app.config['DATABASE_URI'])
            tpl_table = db[TEMPLATE_TABLE]
            if not tpl_table.find_one(tpl_id=template.id) is None:
                if must_return_bool:
                    return False
                else:
                    return error(13, 'template id already exists...')
            else:
                tpl_table.insert(template.to_dict())

            # Template storage
            template_folder = app.config['TEMPLATE_FOLDER']
            if not os.path.exists(template_folder):
                os.makedirs(template_folder)

            f.save(os.path.join(template_folder, template.id))
            if must_return_bool:
                return True
            else:
                return success('template added', {'tpl_id': template.id, 'edit_hash': template.edit_hash})
        else:
            if must_return_bool:
                return False
            else:
                return error(10, 'missing template')
    else:
        if must_return_bool:
            return False
        else:
            return error(2, 'access denied')

@app.route('/template/<tpl_id>', methods=['GET'])
def template_details(tpl_id):
    db = dataset.connect(app.config['DATABASE_URI'])
    tpl_table = db[TEMPLATE_TABLE]
    tpl_row = tpl_table.find_one(tpl_id=tpl_id)
    if tpl_row  is None:
        return error(20, 'unexisted template.')

    result = tpl_row_to_dict(tpl_row)
    return success('template details', result)

def tpl_row_to_dict(tpl_row):
    result = {}
    result['b_id'] = tpl_row['id']
    result['tpl_id'] = tpl_row['tpl_id']
    result['name'] = tpl_row['name']
    result['description'] = tpl_row['description']
    result['author'] = tpl_row['author']
    return result

@app.route('/template/<tpl_id>', methods=['POST'])
def upload_template_package(tpl_id):
    db = dataset.connect(app.config['DATABASE_URI'])
    tpl_table = db[TEMPLATE_TABLE]
    tpl_row = tpl_table.find_one(tpl_id=tpl_id)
    if tpl_row  is None:
        return error(20, 'unexisted template.')

    can_anyone_upload = app.config['ANYONE_CAN_UPLOAD']
    can_upload = False

    candidate = request.form.get('secret')
    can_upload = candidate == app.config['ADMIN_SECRET']

    if can_anyone_upload and not can_upload:
        candidate = request.form.get('edit_hash')
        can_uplad = candidate == tpl_row['edit_hash']

    if not can_upload:
        return error(2, 'access denied')

    f = request.files.get('data')
    if f:
        # Template creation/validation
        template = Template()
        try:
            template.init_with_zip(f)
        except:
            return error(21, 'invalid template')
        if not template.check_valid_id():
            return error(22, 'invalid template id')

        if not template.id == tpl_row['tpl_id']:
            return error(23, 'invalid template id')

        # Template insertion in database
        db = dataset.connect(app.config['DATABASE_URI'])
        tpl_table = db[TEMPLATE_TABLE]

        tpl_table.update(template.to_dict(), ['tpl_id'])

        # Template storage
        template_folder = app.config['TEMPLATE_FOLDER']
        f.save(os.path.join(template_folder, template.id + '.zip'))
        return success('template added', {'tpl_id': template.id, 'edit_hash': template.edit_hash})
    else:
        return error(24, 'missing template')


@app.route('/template/<tpl_id>.zip', methods=['GET'])
def download_template_package(tpl_id):
    db = dataset.connect(app.config['DATABASE_URI'])
    tpl_table = db[TEMPLATE_TABLE]
    if tpl_table.find_one(tpl_id=tpl_id) is None:
        abort(404)

    filename = tpl_id + '.zip'

    template_folder = app.config['TEMPLATE_FOLDER']
    zip_path = os.path.join(template_folder, filename)
    if not os.path.exists(zip_path):
        abort(404)

    return send_from_directory(template_folder, filename, as_attachment=True)


def error(code, msg):
    return json.dumps({'success': False, 'code': code, 'error': msg})

def success(msg, extra_data):
    result = {'success': True}
    if not extra_data is None:
        result['data'] = extra_data

    return json.dumps(result)

if __name__ == "__main__":
    app.run()
