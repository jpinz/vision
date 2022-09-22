import os
import uuid
import json
import base64
import logging
from io import BytesIO

from azure.storage.blob import BlobServiceClient
from msrest.authentication import ApiKeyCredentials

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry, ImageFileCreateBatch

import azure.functions as func

# for storage in blob
base_folder = 'data'
storageConnectionString = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
storageContainer = os.environ["StorageContainer"]

# for pushing to customvision
trainingKey = os.environ["TrainingKey"]
apiEndpoint = os.environ["ApiEndpoint"]
projectId = os.environ["ProjectId"]
tags = {}

def check_tags(trainer: CustomVisionTrainingClient) -> None:
    t = ['no-face', 'bite', 'no-bite']
    etags = { t.name: t for t in trainer.get_tags(projectId) }
    for tag in t:
        if tag in etags:
            tags[tag] = etags[tag]
        else:
            tags[tag] = trainer.create_tag(projectId, tag)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    logging.info(f'Method: {req.method}')
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204,                             
                             headers={ 
                                 'Access-Control-Allow-Headers': 'content-type',
                                 'Access-Control-Allow-Methods': 'POST',
                                 'Access-Control-Max-Age': '180',
                                 'Access-Control-Allow-Origin': '*' })

    body = req.get_json()

    blob_service = BlobServiceClient.from_connection_string(conn_str=storageConnectionString)

    # prep trainer
    credentials = ApiKeyCredentials(in_headers={"Training-key": trainingKey})
    trainer = CustomVisionTrainingClient(apiEndpoint, credentials)

    #check tags
    check_tags(trainer)

    records = { 'images': [] }
    image_list = []

    try:
        for item in body['items']:
            # pose
            pose = item['type'].strip()

            # image bits
            img = base64.b64decode(item['image'].replace('data:image/png;base64,', ''))
            stream = BytesIO(img)

            # storage path + save
            image_name = f'{str(uuid.uuid4())}.png'
            blob_name = f'{base_folder}/{pose}/{image_name}'            
            blob_client = blob_service.get_blob_client(storageContainer, blob_name)
            sresponse = blob_client.upload_blob(stream)

            logging.info(f'Storage Response: {sresponse}')

            # save to custom vision
            image_list.append(ImageFileCreateEntry(name=image_name, contents=img, tag_ids=[tags[pose].id]))


            # return image
            path = f'{blob_service.scheme}://{blob_service.primary_endpoint}/{storageContainer}/{blob_name}'
            records['images'].append({'pose': pose, 'path': path })

        # save list
        upload_result = trainer.create_images_from_files(projectId, ImageFileCreateBatch(images=image_list))
        if not upload_result.response.status_code == 200 and not upload_result.response.status_code == 207:
            records['error'] = {
                'type': 'CustomVision Error',
                'items': []
            }
            for image in upload_result.images:
                records['error']['items'].append({
                    image.source_url: image.status
                })
        else:
            records['error'] = { }
    except Exception as error:
        logging.exception('Python Error')
        records['error'] = { 
            'code': '500',
            'message': f'{type(error).__name__}: {str(error)}',
            'type': 'Python Error'
        }


    return func.HttpResponse(body=json.dumps(records),
                             status_code=200,                             
                             headers={ 'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*' })
