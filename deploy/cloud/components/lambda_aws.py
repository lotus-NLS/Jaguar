import boto3
import inspect
import io
import zipfile
import os, tempfile, shutil, sys
import subprocess

from .enums import AWSRegions
# ----------------------------------------------

class LambdaManager:
    def __init__(self, region : AWSRegions):
        self.region : str = region.value
        self.lambda_client = boto3.client('lambda', region_name=self.region)


    def deploy_lambda_function(self, lambda_name: str, role_arn: str, handler: str, module_code: str):
        try:

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr('backup_repo.py', module_code)


            response = self.lambda_client.create_function(
                FunctionName=lambda_name,
                Runtime='python3.10',
                Role=role_arn,
                Handler=handler,
                Code={'ZipFile': zip_buffer.getvalue()},
            )

            print(f"Lambda function deployed: {lambda_name}")
            return response['FunctionArn']

        except Exception as e:
            print(f"An error occurred: {e}")


    def deploy_lambda_function_new(self,the_function : callable, role_arn : str):
        """
        Deploys a lambda for an entirely self contained function the_function
        Necessary imports must be stated within the function body not in the header of the module
        """

            # Path to site-packages in venv
            # site_packages = os.path.join(venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}',
            #                              'site-packages')
            #
            # # Copy site-packages contents to the temporary directory
            # shutil.copytree(site_packages, os.path.join(tmp_dir, 'site-packages'), dirs_exist_ok=True)
            # shutil.copy2(python_file_path, tmp_dir)
            #
            # # Create a zip file from the temporary directory
            # zip_path = shutil.make_archive('lambda_package', 'zip', tmp_dir)



        try:
            funct_name = the_function.__name__
            zip_content = self.get_zip(the_function=the_function)

            response = self.lambda_client.create_function(
                FunctionName=funct_name,
                Runtime='python3.10',
                Role=role_arn,
                Handler=f'pyfunct.{funct_name}',
                Code={'ZipFile': zip_content},
            )

            print(f"Lambda function deployed: {funct_name}")
            return response['FunctionArn']


        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def get_zip(self, the_function : callable):
        funct_name = the_function.__name__
        python_src = inspect.getsource(the_function)

        with tempfile.TemporaryDirectory() as tmp_dir:

            # make src folder and python script
            srcdir_name = 'srcdir'
            os.makedirs(srcdir_name,exist_ok=True)
            python_file_name = f"{funct_name}.py"
            python_file_path = os.path.join(tmp_dir,srcdir_name, python_file_name)
            with open(python_file_path, 'w') as python_file:
                python_file.write(python_src)


            # setup venv
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            venv_python = os.path.join("venv", "bin", "python")
            subprocess.run([venv_python, "-m", "pip", "install", "pipreqs"], check=True)

            # Install generate requirements and install
            subprocess.run(["pipreqs", srcdir_name], check=True)
            command = f"source venv/bin/activate && pip install -r {srcdir_name}/requirements.txt"
            subprocess.run(command, shell=True, executable='/bin/bash', check=True)

            # package venv
            site_packages = os.path.join('venv', 'lib',
                                         f'python{sys.version_info.major}.{sys.version_info.minor}',
                                         'site-packages')

            # Copy site-packages contents to the temporary directory
            shutil.copytree(site_packages, os.path.join(tmp_dir, 'site-packages'), dirs_exist_ok=True)

            zip_path = shutil.make_archive('lambda_package', 'zip', tmp_dir)
            with open(zip_path, 'rb') as zip_file:
                zip_content = zip_file.read()

        return zip_content


    # def schedule_lambda_backup(self, function_arn: str, schedule_expression: str):
    #     try:
    #         rule_response = self.events_client.put_rule(
    #             Name='github_backup_rule',
    #             ScheduleExpression=schedule_expression,  # e.g., 'rate(1 day)'
    #             State='ENABLED',
    #         )
    #
    #         self.events_client.put_targets(
    #             Rule='github_backup_rule',
    #             Targets=[{'Id': '1', 'Arn': function_arn}]
    #         )
    #
    #         print(f"Scheduled Lambda for GitHub backups with rule: {rule_response['RuleArn']}")
    #     except Exception as e:
    #         print(f"An error occurred: {e}")




# from deploy.cloud.autorun_scripts.backup_repo import do_backup
# import inspect
# # Extract the source code of the function
# function_source = inspect.getsource(do_backup)
# print(function_source)