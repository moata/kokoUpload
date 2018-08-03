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
docker build -t kokoUpload:latest .
```

Run Docker Container 

```
docker run  -e APPLICATION_SETTINGS="./config.cfg" -v uploadedFiles:/app/uploadedFiles/  -p 5000:5000 kokoUpload
```






#### TO DO
- [] Authentication and Authorization 
