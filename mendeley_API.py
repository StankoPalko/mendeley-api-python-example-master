import json
import requests
import helpers

class API_requester(object):

    def get_all_documents(self, token):

        url = 'https://api.mendeley.com/documents'
        headers = {'Authorization': 'Bearer ' + token}
        r = requests.get(url, headers=headers)
        print("Getting All documents:")
        print(r.headers['Link'])
        documents = r.json()

        get_url_from_header,url = helpers.get_url_from_header(r)

        while(get_url_from_header):
            r = requests.get(url, headers=headers)
            get_url_from_header,url = helpers.get_url_from_header(r)
            documents = documents + r.json()

        return documents

    def get_folder_ids(self,token):

        url = 'https://api.mendeley.com/folders'
        headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.mendeley-folder.1+json','Content-Type' : 'application/vnd.mendeley-folder.1+json'}
        r = requests.get(url, headers=headers)

        r = r.json()

        print("This is R:")
        print(r)

        return r

    def get_files(self,token):

        url = 'https://api.mendeley.com/files'
        headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.mendeley-file.1+json'}
        r = requests.get(url, headers=headers)

        files = r.json()

        if (r.headers.__contains__('Link')):
            get_url_from_header,url = helpers.get_url_from_header(r)

            while(get_url_from_header):
                r = requests.get(url, headers=headers)
                get_url_from_header,url = helpers.get_url_from_header(r)
                files = files + r.json()

        print("This is FILES:")
        print(files)

        return files

    def get_documents_in_folder(self,id,token):

        url = 'https://api.mendeley.com/folders/'+ id +'/documents'
        headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.mendeley-document.1+json'}

        r = requests.get(url, headers=headers)

        #print(r.text)

        document_ids = r.json()


        if (r.headers.__contains__('Link')):
            get_url_from_header,url = helpers.get_url_from_header(r)

            while(get_url_from_header):
                r = requests.get(url, headers=headers)
                get_url_from_header,url = helpers.get_url_from_header(r)
                document_ids = document_ids + r.json()

        ids = []

        for r_str in document_ids:
            ids.append(r_str['id'])

        print("Docs in folder: " + str(id) +" Pocet: "+ str(len(ids)) +" Ids:")
        print(ids)

        return ids

    def download_document_by_id(self, file, token,config):

        if file['mime_type']=='application/pdf':
            print("File ID: " + file['id'])
            print("File Doc: " + file['document_id'])
            print("--------------------------:")
            url = 'https://api.mendeley.com/files/'+file['id']
            headers = {'Authorization': 'Bearer ' + token}

            r = requests.get(url, headers=headers)
            with open(config['path'] + file['document_id'] + ".pdf", 'wb') as f:
                    f.write(r.content)
                    f.close()
            return True
        else:
            return False