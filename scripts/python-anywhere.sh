python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
pip install uvicorn
uvicorn app:app --port 1605 --workers 2

#check if the server supports the pinecone env
# If u r getting max retries  for pinecone api connect
#urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='controller.asia-southeast1-gcp-free.pinecone.io', port=443): Max retries exceeded with url: /databases (Caused by NewCon
# try ping controller.asia-southeast1-gcp-free.pinecone.io
# check the ip location with curl ipinfo.io
# delete and create new project for this location
