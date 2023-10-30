from setuptools import setup, find_packages

setup(
    name='pyWebDev',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'Flask',
    ],
    author='Daniel Hollarek',
    description='Substitute HTML, JS and CSS with pure Python',
)