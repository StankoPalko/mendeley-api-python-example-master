from flask import Flask, redirect, render_template, request, session
import yaml
import mendeley_API
import os
import DataGetter
from mendeley import Mendeley
from mendeley.session import MendeleySession
from threading import Thread
from threading import Lock
import _thread

from user_manager import user_manager

with open(os.path.dirname(os.path.abspath(__file__))+'\config.yml') as f:
    config = yaml.load(f)

REDIRECT_URI = config['REDIRECT_URI']

app = Flask(__name__)
app.debug = True
app.secret_key = config['clientSecret']

mendeley = Mendeley(config['clientId'], config['clientSecret'], REDIRECT_URI)

mend_API = mendeley_API.API_requester()
data_getter = DataGetter.data_getter(config)

usr_mngr = user_manager(data_getter,mend_API)
lock = Lock()

@app.route('/')
def home():
    if 'token' in session:
        #return redirect('/userSaved')
        return redirect('/thankyou')
    auth = mendeley.start_authorization_code_flow()
    state = auth.state

    session['state'] = state

    return render_template('home.html', login_url=(auth.get_login_url()))

@app.route('/oauth')
def auth_return():

    auth = mendeley.start_authorization_code_flow(state=session['state'])
    mendeley_session = auth.authenticate(request.url)

    session.clear()
    session['token'] = mendeley_session.token
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:" + session['token']['access_token'])
    print("Token:" + str(session['token']))
    #return redirect('/userSaved')
    return redirect('/thankyou')

@app.route('/userSaved')
def user_saved():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    name = mendeley_session.profiles.me.display_name
    id = mendeley_session.profiles.me.id

    print("User Name: " + name + " Id: " + id )
    #create_directory(str(name))

    token = session['token']['access_token']

    usr_id = usr_mngr.save_user(name,id)

    print("user Id: " + str(usr_id))

    usr_mngr.set_token(token)

    #usr_mngr.save_documents(usr_id)
    #usr_mngr.save_folders(usr_id)

    return render_template('saved.html', saved = name)

@app.route('/listDocuments')
def list_documents():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    name = mendeley_session.profiles.me.display_name
    print("User Name: " + name)
    create_directory(str(name))
    docs = mendeley_session.documents.list(view='client').items

    return render_template('library.html', name=name, docs=docs)

@app.route('/document')
def get_document():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    document_id = request.args.get('document_id')
    doc = mendeley_session.documents.get(document_id)

    return render_template('metadata.html', doc=doc)

@app.route('/metadataLookup')
def metadata_lookup():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    doi = request.args.get('doi')
    doc = mendeley_session.catalog.by_identifier(doi=doi)

    return render_template('metadata.html', doc=doc)


@app.route('/download')
def download():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    document_id = request.args.get('document_id')

    print("Document ID:" + document_id)
    doc = mendeley_session.documents.get(document_id)
    doc_file = doc.files.list().items[0]
    print("Download URL:" + str(doc_file.download_url))
    return redirect(doc_file.download_url)

@app.route('/thankyou')
def thankyou():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    name = mendeley_session.profiles.me.display_name
    id = mendeley_session.profiles.me.id

    print("User Name: " + name + " Id: " + id )
    #create_directory(str(name))

    token = session['token']['access_token']

    if usr_mngr.user_exists(id) == None:
        usr_id = usr_mngr.save_user(name,id)
    else:
        return redirect('/logout')
    print("user Id: " + str(usr_id))


    #thr = Thread(target=usr_mngr.save_all, args=[usr_id,lock])
    #thr.start()
    tuple = (usr_id,lock,token,config)
    _thread.start_new_thread(usr_mngr.save_all,tuple)
    #usr_mngr.save_documents(usr_id)
    #usr_mngr.save_folders(usr_id)

    session.pop('token', None)
    return render_template('thankYou.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    return render_template('thankYou.html')
    #return redirect('/')

@app.route('/test')
def test():
    if 'token' not in session:
        return redirect('/')

    token = mend_API.get_token(str(session['token']))
    id = mend_API.get_folder_ids(token)
    ids = mend_API.get_documents_in_folder(id[0]['id'], token)
    mend_API.download_document_by_id(ids[0], token)

    return redirect('/')

@app.route('/listAllDocuments')
def list_all_documents():
    if 'token' not in session:
        return redirect('/')

    token = mend_API.get_token(str(session['token']))
    mend_API.get_all_documents(token)

    return redirect('/')
#--------------FUNCTIONS

def get_session_from_cookies():
    return MendeleySession(mendeley, session['token'])

def create_directory(name):
    base_path = "C:/Users/Stanko/PycharmProjects/mendeley-api-python-example-master/Users/"
    if not os.path.isdir(base_path + name):
         print("Creating Files")
         os.makedirs(base_path + name)
         os.makedirs(base_path + name + "/PDFs")
         os.makedirs(base_path + name + "/TXTs")

def download_pdfs(ids):
    mendeley_session = get_session_from_cookies()

    document_id = ids

    print(document_id)
    doc = mendeley_session.documents.get(document_id)
    doc_file = doc.files.list().items[0]
    print(str(doc_file.download_url))

if __name__ == '__main__':
    app.run()
