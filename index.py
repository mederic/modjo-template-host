from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/template', methods=['GET'])
def templateList():
    return "List"

@app.route('/template/<int:template_id>', methods=['GET'])
def templateDetails(template_id):
    return "details"

@app.route('/template/<int:template_id>/package', methods=['GET', 'POST'])
def templatePackage(template_id):    
    if request.method == 'POST':
        return uploadTemplatePackage(template_id)
    else:
        return downloadTemplatePackage(template_id)

def uploadTemplatePackage(template_id):
    return "upload"

def downloadTemplatePackage(template_id):
    return "download"

if __name__ == "__main__":
    app.run()
