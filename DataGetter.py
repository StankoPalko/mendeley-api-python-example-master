import psycopg2

class data_getter(object):

    def __init__(self,config):
       self.conn = psycopg2.connect(database = config['database'], user=config['user'], password=config['password'], host=config['host'], port=config['port'])
       self.cur = self.conn.cursor()

    def get_user(self,mendeley_id):

        id = None

        self.cur.execute("SELECT id FROM dp_application.users WHERE users.mendeley_id = '"+ mendeley_id +"'")
        rows = self.cur.fetchall()

        return rows

    def insert_user(self,name,mendeley_id):
        id = None
        try:
            self.cur.execute("INSERT INTO dp_application.users (name,mendeley_id) VALUES (%s,%s) RETURNING id",(str(name),mendeley_id,))
            id = self.cur.fetchone()[0]
        except psycopg2.Error as e:
            print(" Failed to insert User")
            print (e.diag.message_detail)
        self.conn.commit()
        return id

    def insert_document(self,user_id,mendeley_id,title,doi,url):

        self.cur.execute("INSERT INTO dp_application.documents (user_id,mendeley_id,title,doi,url) VALUES(%s, %s, %s, %s, %s)",(user_id,mendeley_id,title,doi,url))
        self.conn.commit()

    def insert_folder(self,user_id,mendeley_id,parent_id,name):

        self.cur.execute("INSERT INTO dp_application.folders (name,parent_id,mendeley_id,user_id) VALUES(%s, %s, %s, %s) RETURNING folder_id",(name,parent_id,mendeley_id,user_id,))
        id = self.cur.fetchone()[0]
        self.conn.commit()

        return id

    def update_document(self,user_id,doc_id,folder_id):

        self.cur.execute("UPDATE dp_application.documents SET folder_id =(%s) WHERE user_id = (%s) AND mendeley_id = (%s)", (folder_id,user_id,doc_id))
        self.conn.commit()

    def update_document_has_file(self,user_id,doc_id,has_file):

        self.cur.execute("UPDATE dp_application.documents SET has_file =(%s) WHERE user_id = (%s) AND  mendeley_id = (%s)", (has_file,user_id,doc_id))
        self.conn.commit()




