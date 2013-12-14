import re
import uuid
import xml.etree.ElementTree as ET

from zipfile import *

class Template:

    def init_with_zip(self, zip_file):
        template = ZipFile(zip_file)
        for name in template.namelist():
            print name

        manifest = template.open('modjoManifest.xml')
        tree = ET.parse(manifest)
        root = tree.getroot()
        metadata = root.find('metadata')

        self.id = metadata.find('id').text
        self.name = metadata.find('name').text
        self.description = metadata.find('description').text

        author = metadata.find('author')
        if not author is None:
            self.author = author.text
        else:
            self.author = None

        self.edit_hash = uuid.uuid4().hex

        manifest.close()
        template.close()
        zip_file.seek(0)

    def check_valid_id(self):
        return re.match('^[A-Za-z0-9\.]+$', self.id)

    def to_dict(self):
        result = {}
        result['tpl_id'] = self.id
        result['name'] = self.name
        result['description'] = self.description
        result['author'] = self.author
        result['edit_hash'] = self.edit_hash
        return result;
