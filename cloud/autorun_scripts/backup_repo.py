


def do_backup(event, context):
    import traceback
    import boto3
    import json
    import shutil
    import requests
    import zipfile
    import io
    import os
    from datetime import datetime

    _ = event
    _ = context

    os.chdir(path='/tmp')

    # Get credentials
    client = boto3.client('secretsmanager')
    secret_value = client.get_secret_value(SecretId='github')
    secret = json.loads(secret_value['SecretString'])
    token = secret['token']


    # Make container
    src_dir = 'lotus_src'
    os.makedirs(src_dir, exist_ok=True)

    # Clone repo
    def write_download_content(url : str, fpath : str, headers : dict):
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(fpath)

    try:
        lotus_url = 'https://github.com/Somerandomguy10111/Lotus/archive/HEAD.zip'
        lotus_foldername = 'Lotus'
        lotus_path = os.path.join(src_dir, lotus_foldername)

        pystuff_url = 'https://github.com/Somerandomguy10111/pystuff/archive/HEAD.zip'
        pystuff_foldername = 'pystuff'
        pystuff_path = os.path.join(src_dir, pystuff_foldername)

        auth_headers = {'Authorization': f'token {token}'}

        write_download_content(url=lotus_url,fpath=lotus_path,headers=auth_headers)
        write_download_content(url=pystuff_url,fpath=pystuff_path,headers=auth_headers)

    except Exception as e:
        print(f'Failed to clone repo: {e}')
        print(traceback.format_exc())
        print('Backup failed')


    # Zip it
    the_format = 'zip'
    base_name = 'lotus_backup'
    fname = f'{base_name}.{the_format}'
    shutil.make_archive(base_name=base_name,format=the_format,root_dir=src_dir)

    # Upload it
    current_date = datetime.now()
    date_str = current_date.strftime("%d_%m_%Y")
    s3 = boto3.client('s3')
    s3.upload_file(fname,'thelotusbucket',f'{base_name}_{date_str}.{the_format}')

    print('Backup completed sucessfully')

# do_backup(None, None)