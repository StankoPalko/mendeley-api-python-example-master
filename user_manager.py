import DataGetter
import mendeley_API
import helpers

class user_manager(object):

    def __init__(self,data_getter,API):

        self.data_getter = data_getter # type: DataGetter.data_getter
        self.mend_API = API # type: mendeley_API.API_requester

    def save_documents(self,user_id):

        documents = self.mend_API.get_all_documents(self.token)

        doi = None
        url = None

        for doc in documents:
            print("Name:" + doc['title'] + " ID:" + doc['id'])

            if doc.__contains__('identifiers'):
                if doc['identifiers'].__contains__('doi'):
                    print("Doi:" + doc['identifiers']['doi'])
                    doi = doc['identifiers']['doi']
                    url = helpers.get_link(doi)
            self.data_getter.insert_document(user_id,doc['id'],doc['title'],doi,url)

    def set_token(self,token):
        self.token = token

    def user_exists(self,mendeley_id):
        user = self.data_getter.get_user(mendeley_id)

        if not user:
            id = None
        else:
            id = user[0][0]

        return id

    def save_user(self,name,mendeley_id):

        id =  self.data_getter.insert_user(name,mendeley_id)

        return id

    def save_folders(self,id):

        folders = self.mend_API.get_folder_ids(self.token)

        for fold in folders:
            print("Name:" + fold["name"] + " ID: " + fold["id"])
            if fold.__contains__("parent_id"):
                parent_id = fold["parent_id"]
            else:
                parent_id = None

            fold_id = self.data_getter.insert_folder(id,fold["id"],parent_id,fold["name"])
            folder_docs_ids = self.mend_API.get_documents_in_folder(fold["id"],self.token)
            for doc in folder_docs_ids:
                self.data_getter.update_document(id,doc,fold_id)
    def save_files(self,id,token,config):

        files =  self.mend_API.get_files(token)

        for file in files:
             if self.mend_API.download_document_by_id(file,token,config):
                 self.data_getter.update_document_has_file(id,file['document_id'],1)



    def save_all(self,id,lock,token,config):
        lock.acquire()
        self.set_token(token)
        self.save_documents(id)
        self.save_folders(id)
        self.save_files(id,token,config)
        lock.release()


