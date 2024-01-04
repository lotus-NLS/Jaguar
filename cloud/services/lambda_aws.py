import boto3
import inspect, logging
import os, tempfile, shutil, sys
import subprocess
from distutils.dir_util import copy_tree


from cloud.entities.enums import AWSRegions
# ----------------------------------------------

class LambdaAWS:

    lambda_filename = 'pyfunct'

    def __init__(self, region : AWSRegions):
        self.region : str = region.value
        self.lambda_client = boto3.client('lambda', region_name=self.region)


    def cloud_lambda_function(self, the_function : callable, role_arn : str):
        """
        Creates a lambda for an entirely self contained function the_function
        Necessary imports must be stated within the function body not in the header of the module
        """
        try:
            funct_name = the_function.__name__
            zip_content = self.get_zip(the_function=the_function)

            response = self.lambda_client.create_function(
                FunctionName=funct_name,
                Runtime='python3.10',
                Role=role_arn,
                Handler=f'{LambdaAWS.lambda_filename}.{funct_name}',
                Code={'ZipFile': zip_content},
            )

            logging.info(f"Lambda function created: {funct_name}")
            return response['FunctionArn']


        except Exception as e:
            logging.error(f"An error occurred: {e}",exc_info=True)


    @staticmethod
    def get_zip(the_function : callable):
        python_src = inspect.getsource(the_function)

        with tempfile.TemporaryDirectory() as tmp_dir:

            def make_subdir(rel_path: str):
                subdir_path = os.path.join(tmp_dir, rel_path)
                os.makedirs(subdir_path, exist_ok=True)

            def write_file(rel_path: str, content: str):
                file_path = os.path.join(tmp_dir, rel_path)
                with open(file_path, 'w') as file:
                    file.write(content)

            def run_subprocess(command: list[str], rel_path: str,**kwargs):
                subdir_path = os.path.join(tmp_dir, rel_path)
                subprocess.run(command, cwd=subdir_path, check=True,**kwargs)

            # Create src directory and src file
            src_foldername = 'src'
            make_subdir(rel_path=src_foldername)
            write_file(rel_path=f'src/{LambdaAWS.lambda_filename}.py', content=python_src)

            # Generate venv
            run_subprocess(command=[sys.executable, "-m", "venv", "venv"],rel_path='')
            venv_location = os.path.join("venv", "bin", "python")
            run_subprocess(command=[venv_location, "-m", "pip", "install", "pipreqs"],rel_path='')

            # Install requirements
            run_subprocess(command=[f"source venv/bin/activate && pipreqs {src_foldername}"],
                           rel_path='',
                           shell=True,
                           executable='/bin/bash')
            install_requirements = f"source venv/bin/activate && pip install -r {src_foldername}/requirements.txt"
            run_subprocess(command=[install_requirements],
                           rel_path='',
                           shell=True,
                           executable='/bin/bash')

            site_package_location = os.path.join(tmp_dir,'venv', 'lib',
                                                 f'python{sys.version_info.major}.{sys.version_info.minor}',
                                                 'site-packages')
            shutil.copytree(site_package_location,
                            os.path.join(tmp_dir,src_foldername,'site-packages'),
                            dirs_exist_ok=True)

            from_directory = site_package_location
            to_directory = os.path.join(tmp_dir,src_foldername)
            copy_tree(from_directory, to_directory)

            zip_path = shutil.make_archive(base_name=os.path.join(tmp_dir, 'lambda_package'),
                                           format='zip',
                                           root_dir=os.path.join(tmp_dir,src_foldername))
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

