#!/home/mineracao/documentos/Sistema-hibrido-com-interface/alan/SistemaHibrido/env/bin/python

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import sys

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def download_dump_mysql(service):
    frase = "name contains '<frase para encontrar o backup do banco>'"
    # Call the Drive v3 API
    results = service.files().list(q=frase,
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    print(results)

    import io
    from googleapiclient.http import MediaIoBaseDownload
    # if you get the shareable link, the link contains this id, replace the file_id below
    file_id = results['files'][0]['id']
    request = service.files().get_media(fileId=file_id)
    # replace the filename and extension in the first field below
    fh = io.FileIO('banco.zip', mode='w')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

def upload_dump_mongo(service):
    from googleapiclient.http import MediaFileUpload
    from datetime import datetime
    folder_id = '<id da pasta que receberá o dump>'
    file_metadata = {'name': 'dump_'+ datetime.now() + '.zip', 'parents': [folder_id]}
    media = MediaFileUpload('<nome do zip do dump>.zip', resumable=True)
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print('File ID: %s' % file.get('id'))

def main():
    """Autenticação de utilização da API do drive
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    # para obter o arquivo credentials.json valido é preciso ir ao console do google drive criar um projeto baixo-lo
    # e coloca-lo neste diretório
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

if __name__ == '__main__':
    service = main()
    jobs = {"download": download_dump_mysql, "upload": upload_dump_mongo}
    choosen = sys.argv[1]
    jobs[choosen]()
