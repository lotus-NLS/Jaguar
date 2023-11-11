import os


def do_backup(event, context):
    import boto3
    import json
    import shutil
    from git import Repo
    from datetime import datetime

    _ = event
    _ = context

    # Get credentials
    client = boto3.client('secretsmanager')
    secret_value = client.get_secret_value(SecretId='github')
    secret = json.loads(secret_value['SecretString'])
    username = secret['name']
    token = secret['token']

    # Make container
    src_dir = 'lotus_src'
    os.makedirs(src_dir, exist_ok=True)

    # Clone repo

    try:
        lotus_foldername = 'Lotus'
        Repo.clone_from(url='https://github.com/Somerandomguy10111/Lotus',
                        to_path=os.path.join(src_dir,lotus_foldername),
                        env={'GIT_USERNAME': username, 'GIT_PASSWORD': token})

        pystuff_foldername = 'pystuff'
        Repo.clone_from(url='https://github.com/Somerandomguy10111/pystuff',
                        to_path=os.path.join(src_dir,pystuff_foldername),
                        env={'GIT_USERNAME': username, 'GIT_PASSWORD': token})

    except Exception as e:
        print(f'Failed to clone repo: {e}')
        return {"message": "Backup failed"}

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

    print(f'Done')
    return {"message": "Backup completed successfully"}


do_backup(None, None)