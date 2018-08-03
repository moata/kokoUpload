import os
from base64 import urlsafe_b64encode
from uuid import uuid4

from flask import Flask, abort, jsonify, request, send_from_directory 
from werkzeug.utils import secure_filename

from flask_script import Manager, Server 
import pickle

import hashlib
hasher = hashlib.sha1()

api = Flask(__name__)
api.config.from_envvar('APPLICATION_SETTINGS')



if not os.path.exists(api.config['UPLOAD_DIR']):
    os.makedirs(api.config['UPLOAD_DIR'])


# calculate checksum for a file 
def genCheckSumForFiles(names,root):
    
    with open(os.path.join(root,names),'rb') as afile:
        buf = afile.read(api.config['BLOCKSIZE'])
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(api.config['BLOCKSIZE'])
    return hasher.hexdigest()

# calculate a checksum for data string
def genCheckSum(uploadedFile):
    return hashlib.sha1(uploadedFile.read()).hexdigest()
            
    
def checkSumCalc(dbFile):
    try:
        for root,dirs,files in os.walk(api.config['UPLOAD_DIR']):
            for names in files:
                fileUUID=names.rsplit('.', 1)[0]
                if fileUUID in dbFile:
                    pass
                else:
                    md5 = genCheckSumForFiles(names,root)
                    
                    dbFile.update({md5:fileUUID})
                    output = open("db.pkl","wb")
                    pickle.dump(dbFile,output)
                    output.close()

        pkl_file = open('db.pkl', 'rb')
        mydict = pickle.load(pkl_file)
        pkl_file.close()
        print mydict
    except:
        pass
    

def checkSumDbFile():
    try:
        dbFile = pickle.load(open("db.pkl","rb"))
        checkSumCalc(dbFile)
    except (OSError, IOError) as e:
        foo = {'a':0}
        pickle.dump(foo,open("db.pkl","wb"))
        dbFile = pickle.load(open("db.pkl","rb"))
        checkSumCalc(dbFile)

# Create a custom server to calculate checksum before start receiving request.
class CustomServer(Server):
    def __call__(self,app,*args,**kwargs):
        checkSumDbFile()
        return Server.__call__(self,app,*args,**kwargs)

manager = Manager(api)
manager.add_command('runserver',CustomServer(host=api.config['HOST'],port=api.config['PORT']))



# check if file extention is allowed 
def allowed_file(filename):
    extension = filename.rsplit('.', 1)[1]
    return extension,'.' in filename and extension.lower() in api.config['ALLOWED_EXTENSIONS']




# List files on the server 
@api.route('/files')
def list_files():
    files = []
    for filename in os.listdir(api.config['UPLOAD_DIR']):
        path = os.path.join(api.config['UPLOAD_DIR'],filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

# Download a file
@api.route('/files/<path:path>')
def get_file(path):
    return send_from_directory(api.config['UPLOAD_DIR'],path,as_attachment=True)

# Upload a file
@api.route('/files/<filename>',methods=['POST'])
def post_file(filename):
    
    if '/' in filename:
        abort(400,'no subdirectories allowed !')
    
    # calculate hash for income data
    requestMD5 = hashlib.sha1(request.data).hexdigest()

    # check if extension allowed , otherwise return 400 not allowed !
    extension,allowed = allowed_file(filename)
    if allowed:
        # open the database file to check if this hash already exists
        output = pickle.load(open("db.pkl","rb"))
        if requestMD5 in output:
            return output[requestMD5]+'\n',201
        else:
            # generate uuid for the new file 
            Nfilename = urlsafe_b64encode(uuid4().bytes).decode("ascii").rstrip("=")
            with open(os.path.join(api.config['UPLOAD_DIR'],Nfilename+"."+extension),'wb') as fp:
                fp.write(request.data)
            # upload the checksum in database file 
            output.update({requestMD5:Nfilename+"."+extension})
            output2 = open("db.pkl","wb")
            pickle.dump(output,output2)
            output2.close()
        return Nfilename+"."+extension+'\n',201
    else:
        return abort(400,'not allowed extension')


if __name__ == '__main__':
    manager.run()