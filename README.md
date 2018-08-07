# kokoUpload
kokoUpload is simple HTTP API to upload / download and list files using Flask 
#### Features
 * Upload Files
 * Download Files
 * List Files
 * Calculate Hash for each file, to use existing contant

#### Usage
You need docker to be installed locally.

Clone project
```
git clone https://github.com/moata/kokoUpload.git
```

Build Docker image 
```
docker build -t kokoupload:latest .
```

Run Docker Container 

```
docker run  -e APPLICATION_SETTINGS="./config.cfg" -v uploadedFiles:/app/uploadedFiles/  -p 5000:5000 kokoupload
```

Upload File 
```
curl -X POST http://127.0.0.1:5000/files/test.txt -T test.txt
```

Download File
```
curl http://127.0.0.1:5000/files/XXXXXXX.gif
```

List Files
```
curl http://127.0.0.1:5000/files
```

Delete File
```
curl http://127.0.0.1:5000/files/del/XXXXXXXX.gif
```
#### TO DO
- [] Authentication and Authorization 
