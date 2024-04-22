from flask import Flask, request, render_template, jsonify
from langchain_community.document_loaders import DirectoryLoader
from dotenv import load_dotenv

import os
from dotenv import load_dotenv
from utils import *

load_dotenv()

global db_chain

app = Flask(__name__)

@app.route('/',methods=["Get","POST"])
def home():
    df = ["a","b","c"]
    return render_template("index.html",tables=df)

@app.route('/set_params_session',methods=["GET","POST"])
def set_params_session():
    global dataDirectory
    dataDirectory = request.form["dataDirectory"]
    
    df_json_metadata, df_raw_text=create_docs(dataDirectory)
   
    # return render_template('invoice_metadata.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
    return render_template('invoice_metadata.html',  df=df_json_metadata, df_raw_text=df_raw_text )

if __name__ == "__main__":
    app.run(debug=True)