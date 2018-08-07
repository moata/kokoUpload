import os
from base64 import urlsafe_b64encode
from uuid import uuid4

from flask import Flask, abort, jsonify, request, send_from_directory 
from werkzeug.utils import secure_filename


import pickle

import hashlib
hasher = hashlib.sha1()

BLOCKSIZE=65536
UPLOAD_DIR = '/app/uploadedFiles/'

# calculate checksum for a file 
def genCheckSumForFiles(names,root):
    with open(os.path.join(root,names),'rb') as afile:
        try:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        except:
            print 'ERROR: Reading file !'
    return hasher.hexdigest()

def checkSumCalc(dbFile):
    try:
        for root,dirs,files in os.walk(UPLOAD_DIR):
            for names in files:
                if names in dbFile:
                    print 'already there !'
                else:
                    md5 = genCheckSumForFiles(names,root)
                    
                    dbFile.update({md5:names})
                    output = open("db.pkl","wb")
                    pickle.dump(dbFile,output)
                    output.close()

        pkl_file = open('db.pkl', 'rb')
        mydict = pickle.load(pkl_file)
        pkl_file.close()
    except:
        pass
    

def checkSumDbFile():
    try:
        dbFile = pickle.load(open("db.pkl","rb"))
        checkSumCalc(dbFile)
        return Flask(__name__) 
    except (OSError, IOError) as e:
        foo = {'a':0}
        pickle.dump(foo,open("db.pkl","wb"))
        dbFile = pickle.load(open("db.pkl","rb"))
        checkSumCalc(dbFile)
        return Flask(__name__)

api = checkSumDbFile()
api.config.from_envvar('APPLICATION_SETTINGS')



if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)




# calculate a checksum for data string
def genCheckSum(uploadedFile):
    return hashlib.sha1(uploadedFile.read()).hexdigest()
            


# check if file extention is allowed 
def allowed_file(filename):
    extension = filename.rsplit('.', 1)[1]
    return extension,'.' in filename and extension.lower() in api.config['ALLOWED_EXTENSIONS']



# Delete file
@api.route('/files/del/<filename>',strict_slashes=False)
def delete_file(filename):
    if os.path.exists(os.path.join(UPLOAD_DIR,filename)):
        try:
            os.remove(os.path.join(UPLOAD_DIR,filename))
            dbFile = pickle.load(open("db.pkl","wb"))
            for key, value in dbFile.iteritems():
                if filename == value:
                    del dbFile[value]
                    output2 = open("db.pkl","wb")
                    pickle.dump(dbFile,output2)
                    output2.close()
            return 'Deleted\n',201
        except:
            return 'Not able to delete',403
    else:
        return 'File not exists ',404

# List files on the server 
@api.route('/files',strict_slashes=False)
def list_files():
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR,filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

# Download a file
@api.route('/files/<path:path>',strict_slashes=False)
def get_file(path):
    return send_from_directory(UPLOAD_DIR,path,as_attachment=True)

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
            return "http://"+request.host+"/files/"+output[requestMD5]+'\n',201
        else:
            # generate uuid for the new file 
            Nfilename = urlsafe_b64encode(uuid4().bytes).decode("ascii").rstrip("=")
            with open(os.path.join(UPLOAD_DIR,Nfilename+"."+extension),'wb') as fp:
                fp.write(request.data)
            # upload the checksum in database file 
            output.update({requestMD5:Nfilename+"."+extension})
            output2 = open("db.pkl","wb")
            pickle.dump(output,output2)
            output2.close()
        return "http://"+request.host+"/files/"+Nfilename+"."+extension+'\n',201
    else:
        return abort(400,'not allowed extension')


if __name__ == '__main__':
    api.run(host=api.config['HOST'],port=api.config['PORT'])
