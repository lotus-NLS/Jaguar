import boto3
import json
import shutil
from git import Repo

# ----------------------------------------------


def backup_github_repo(event, context):
    _ = event
    _ = context

    # Get credentials
    client = boto3.client('secretsmanager')
    secret_value = client.get_secret_value(SecretId='github')
    secret = json.loads(secret_value['SecretString'])
    username = secret['name']
    token = secret['token']

    # Clone repo
    foldername = 'Lotus'
    try:
        Repo.clone_from(url='https://github.com/Somerandomguy10111/Lotus',
                        to_path=foldername,
                        env={'GIT_USERNAME': username, 'GIT_PASSWORD': token})
    except Exception as e:
        print(f'Failed to clone repo: {e}')
        return {"message": "Backup failed"}

    # Zip it
    the_format = 'zip'
    base_name = 'lotus_backup'
    fname = f'{base_name}.{the_format}'
    shutil.make_archive(base_name=base_name,format=the_format,root_dir=foldername)

    # Upload it
    s3 = boto3.client('s3')
    s3.upload_file(fname,'thelotusbucket', fname)

    print(f'Done')
    return {"message": "Backup completed successfully"}

backup_github_repo(None,None)
