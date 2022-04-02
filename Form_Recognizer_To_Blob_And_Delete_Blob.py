# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 08:05:13 2022

@author: btindol
"""

"""
This code sample shows Prebuilt Read operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Form Recognizer Python client library SDKs v3.0
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/quickstarts/try-v3-python-sdk
"""
# INSTALL THESE !!!! 
#pip install azure-ai-formrecognizer==3.2.0b3 # beta version get  DocumentAnalysisClient problem cant find function in library
#pip install azure-core
#pip install azure-storage-blob==0.37.1 
########################################################################################
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import datetime
import os
# pip install azure-storage-blob --upgrade

connect_str = "<Connection String>" # retrieve the connection string from the environment variable

container_name = "/form-recognizer/forms" # container name in which images will be store in the storage account

blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str) # create a blob service client to interact with the storage account

container_client = blob_service_client.get_container_client(container=container_name)

endpoint = "https://eastus.api.cognitive.microsoft.com/"
key = "<Key>"

container = ContainerClient.from_connection_string(conn_str=connect_str, container_name="form-recognizer")#/upload-destination contract-intelligence-arrival
    

blob_list = container.list_blobs(name_starts_with="forms/")#container,prefix="forms/
for blob in blob_list:
    print(blob.name + '\n')
    blobname = blob.name
    newblobname = blobname.replace("forms/", "")
    print("New blob name is: ",newblobname)
    # Make string for formatting 
    unfinishedUrl = "https://stgdacustintelldev001.blob.core.windows.net/form-recognizer/{blobname}" # Faster for development 1 page (WORKS!!)
    print("Unfinished url is: ",unfinishedUrl)

    # complete URL that specific blob
    formUrl = unfinishedUrl.format(blobname=blobname)
    print("Blob full URL is: ",formUrl)

    # This is the document analysis connection client
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
                    
    # Grab that file and do the analysis 
    poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", formUrl)

    # get the results 
    result = poller.result()

    print ("Document contains content: ", result.content)
    
    #     # go into the url in the blob where you want to find your uploaded pdf

    #     # This works one page png from the PPOR1005.pdf
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
    poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", formUrl)
    result = poller.result()

    print ("Document contains content: ", result.content)
    
    # # Writing the results to a text file for later analysis send this to the blob!! 
    dateTimeObj = datetime.now();
    time = str(dateTimeObj.year) + '-'  + str(dateTimeObj.month)  + '-' +  str(dateTimeObj.day) +  '-'+ str(dateTimeObj.hour) +  '-' +  str(dateTimeObj.minute) +  '-' +  str(dateTimeObj.second)
    print("Time is: ",time)

    png_filename = blobname.replace("forms/", "") # remove the directory so the path does send file to another place
    print("With png name: ",png_filename) # to use for delete blob referal 
    blob_name = png_filename.replace(".png", ".txt") # save it to txt file so change .png or pdf to .txt 
    blob_name = blob_name.replace(".pdf", ".txt")
    print("New blob name is: ",blob_name)

    resultname = "CI_FR_{time}_{blob_name}" # CI (Contract intelligence) _ FR (Form Recognizer) Time stamp blob name 
    print("The preformat name is: ",resultname)

    filename = resultname.format(time=time,blob_name=blob_name)
    print("The final file name is: ",filename) 

    # Write the new file name to local txt file destination
    text_file = open("./data/"+filename, "w")#,encoding="utf-8"
    n = text_file.write(result.content)
    text_file.close()
    print("The file is ",text_file)

    # Try to create a local directory to hold blob data if not already made
    try:
        local_path = "./data" # make new folder
        os.mkdir(local_path)
    except:
        pass

    # Create a file in the local data directory to upload and download
    local_file_name = filename  # Take the name that we named the file above and change it to local file name for now
    print("Local file name is :",local_file_name)

    upload_file_path = os.path.join(local_path, local_file_name)
    print("Upload file path is: ",upload_file_path)

    # Pick container name to drop the file into! 
    container_name = "form-recognizer/end-destination" #end-destination  or forms 
    print("Container name is :",container_name)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
    print("The blob client is: ",blob_client)

    print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

    # Upload the created file to end destination now 
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data)

    import time
    time.sleep(10) # Allow the blob to show up in the folder 


    # Make sure you change the container client to the forms directory!!!! 
    container_delete = ContainerClient.from_connection_string(conn_str=connect_str, container_name="form-recognizer/forms")
    container_delete.delete_blob(blob=png_filename)
    print("Deleted blake blob!! ")

    

