#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import shutil
import string
import tempfile
import subprocess

from flask import Flask, make_response, request
from flask.templating import render_template

import configuration

__author__ = 'Jonas Gröger <jonas.groeger@gmail.com>'


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='++',
        variable_end_string='++',
    ))


app = CustomFlask(__name__)
app.config.from_object(configuration)

BASE_DIR = os.path.dirname(__file__)
FILENAME_TEX = 'Vorlage.tex'
FILENAME_PDF = 'Vorlage.pdf'


@app.route('/generate', methods=['POST'])
def generate():
    temp_directory = tempfile.mkdtemp()

    # Write the file
    with open(os.path.join(temp_directory, FILENAME_TEX), 'w', encoding='utf-8') as tex_file:
        s = render_template(FILENAME_TEX,
                            **request.form.to_dict())
        tex_file.write(s)

    # Render
    os.chdir(temp_directory)
    proc = subprocess.Popen(['xelatex', FILENAME_TEX])
    proc.communicate()

    # Get the bytes
    with open(FILENAME_PDF, mode='rb') as pdf_file:
        pdf_bytes = pdf_file.read()

    # Cleanup
    os.chdir(BASE_DIR)
    shutil.rmtree(temp_directory)

    filename_download = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    response = make_response(pdf_bytes)
    response.headers['Content-Disposition'] = "attachment; filename=" + filename_download + '.pdf'
    response.mimetype = 'application/pdf'
    return response


@app.route('/')
def hello_world():
    return render_template('form.html')


if __name__ == '__main__':
    app.run()
