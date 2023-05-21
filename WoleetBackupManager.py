#ceate dump and ziping file 
import json
import yaml
from yaml.loader import SafeLoader
from time import gmtime, strftime
import hashlib
import os
import requests
import sched
import time
import boto3
import zipfile
import pkg_resources
import subprocess


def main():
    yaml_file = open("settings.yaml", 'r')
    settings = yaml.load(yaml_file,Loader=SafeLoader)
    anchor_id = settings["anchor_id"]
    if anchor_id is None or anchor_id == '':
        #Applé la fonction Create essentiels qui recupere les valeur des varuiables (la fonction create_essentials donne les valeures aux variables)
        command_str,filename,backup_path,env = create_essentials()
        #Applé la fonction backup database (la fonction backup_database prend des paramaitres )
        backup_database(command_str,env)# tablenames optionel 
        #applé la fonction hashsha256_database (la fonction hashsh-a256_database donne une valeur a la variable hashDump et prend la valeur de la variable filename depuis main)
        hashDump = hashsha256_database(filename)
        #renommer le fichier dump en hach + filename + .tar et retouner la nom final stocker dan la variable fillenamefinal
        fillenamefinal=renameDumpToHash(filename,hashDump,backup_path)
        SaveFileNameInSettings(fillenamefinal)
        anchor_id=interogateToWoleet(hashDump,fillenamefinal)
        SaveAnchorIdInSettings(anchor_id)
    else :
        while True:
            if statutCheckAnchor():
                break  # Stop running if the condition is True
            # Wait for 6 hours
            time.sleep(6*60*60)
            print('wait')
        
        downloadCertificat()
        saveToS3()     
        #when you get true from statutCheck you should download the certifcat

# récuperation des variable depuis le fichier settings 
def create_essentials():
    yaml_file = open("settings.yaml", 'r')
    settings = yaml.load(yaml_file,Loader=SafeLoader)
    db_name = settings["db_name"]
    db_user = settings["db_user"]
    db_password = settings["db_password"]
    db_host = settings["db_host"]
    db_port = settings["db_port"]
    backup_path = settings["backup_path"]
    filename = settings["filename"]
    filename = filename + "_" + strftime("%Y%m%d") + ".tar"
    #concatiner les variables de la DB

    # Set the environment variable for PGPASSWORD
    env = dict(os.environ, PGPASSWORD="mysecretpassword")

    # Construct the command
    command_str = (
        'pg_dump -h {host} -p {port} -U {username} -F t --no-owner --no-acl --dbname={database} --data-only --schema=public -f {output_file}'
    ).format(
        host=db_host,
        port=db_port,
        username=db_user,
        database=db_name,
        output_file=filename
    )
    
    return command_str,filename,backup_path,env

#dump db 
def backup_database(command_str=None,env=None):
    
    try:
        subprocess.run(command_str, env=env)
        print("Backup completed")
    except Exception as e:
        print ("!!Problem occured!!")
        print (e)

#hashing file sha256 and storage s3

def hashsha256_database(filename=None):
    with open(filename) as f:
        data = f.read()
    hashDump = hashlib.sha256(data.encode('utf-8')).hexdigest()
    SaveHashDumpInSettings(hashDump)
    return hashDump

def renameDumpToHash(filename=None,hashDump=None,backup_path=None): #filename in old name file
    filenamefinal = hashDump + "_" + filename
    os.rename(os.path.join(backup_path, filename), os.path.join(backup_path, filenamefinal))
    return filenamefinal 

# interogate  to wolett + retun id

def interogateToWoleet(hashDump=None,fillenamefinal=None):  
    yaml_file = open("settings.yaml", 'r')
    settings = yaml.load(yaml_file,Loader=SafeLoader)
    token = settings["token"]
    #token = "Basic " + token
    url = "https://api.woleet.io/v1/anchor"

    payload = {
    "name": fillenamefinal,
    "hash": hashDump
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": token
    }
    response = requests.post(url, json=payload, headers=headers)
    json_object = json.loads(response.text)
    anchor_id = json_object["id"]
    return anchor_id

def SaveAnchorIdInSettings(anchor_id=None):
    # Load the YAML file into a Python dictionary
    with open('settings.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Modify the dictionary
        config['anchor_id'] = anchor_id

    # Dump the modified dictionary back into a YAML file
    with open('settings.yaml', 'w') as f:
        yaml.safe_dump(config, f)

def SaveFileNameInSettings(fillenamefinal=None):
    # Load the YAML file into a Python dictionary
    with open('settings.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Modify the dictionary
        config['fillenamefinal'] = fillenamefinal

    # Dump the modified dictionary back into a YAML file
    with open('settings.yaml', 'w') as f:
        yaml.safe_dump(config, f)

def SaveHashDumpInSettings(hash_dump=None):
    # Load the YAML file into a Python dictionary
    with open('settings.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Modify the dictionary
        config['hash_dump'] = hash_dump

    # Dump the modified dictionary back into a YAML file
    with open('settings.yaml', 'w') as f:
        yaml.safe_dump(config, f)

def SaveSignatureIdInSettings(signature_id=None):
    # Load the YAML file into a Python dictionary
    with open('settings.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Modify the dictionary
        config['signature_id'] = signature_id

    # Dump the modified dictionary back into a YAML file
    with open('settings.yaml', 'w') as f:
        yaml.safe_dump(config, f)

def statutCheckAnchor():
    yaml_file = open("settings.yaml", 'r')
    settings = yaml.load(yaml_file,Loader=SafeLoader)
    anchor_id = settings["anchor_id"]
    token = settings["token"]
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": token
    }

    # Set the URL of the Woleet API endpoint for retrieving the status of a certificate by ID
    url = f'https://api.woleet.io/v1/anchor/{anchor_id}'

    # Send the API request to retrieve the certificate status
    response = requests.get(url, headers=headers)
    json_object = json.loads(response.text)
    status = json_object["status"]

    # Check if the API request was successful
    if status == "CONFIRMED":
    # Print the certificate status
        return True
    return False


#returne certificate and storage s3 
def downloadCertificat():
    yaml_file = open("settings.yaml", 'r')
    settings = yaml.load(yaml_file,Loader=SafeLoader)
    anchor_id = settings["anchor_id"]
    fillenamefinal = settings["hash_dump"]
    token = settings["token"]
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": token
    }
    # Configure API endpoint and certificate ID
    api_endpoint = f'https://api.woleet.io/v1/anchor/{anchor_id}/attestation'

    # Make GET request to API endpoint to download certificate
    response = requests.get(api_endpoint, headers=headers)

    # Write certificate content to a file
    with open(fillenamefinal + ".pdf", "wb") as f:
        f.write(response.content)

    

# interogate s3 to store the backUp & the certificat
def saveToS3():
    yaml_file = open("settings.yaml", 'r')
    settings = yaml.load(yaml_file,Loader=SafeLoader)
    hash_dump = settings["hash_dump"]
    AccessKeyId = settings["AccessKeyId"]
    SecretAccessKey = settings["SecretAccessKey"]
    S3BucketName = settings["S3BucketName"]
    #create le zip pour regourpe le certificat et le dump (.tar)
    certificat = hash_dump+".pem"
    dump = hash_dump+".tar"

    # Configure S3 clien
    s3 = boto3.resource(
            service_name='s3',
            region_name='eu-west-1',
            aws_access_key_id=AccessKeyId,
            aws_secret_access_key=SecretAccessKey
        )
    
    # Store the blob to S3
    s3.Bucket(S3BucketName).upload_file(Filename=certificat, Key=certificat)
    s3.Bucket(S3BucketName).upload_file(Filename=dump, Key=dump)



main()
