from setuptools import setup, find_packages

setup(
    name='pywebdev',
    version='0.2',
    packages=['devkit', 'browser'],
    package_dir={'': 'src'},
    install_requires=[
        'flask',
    ],
    author='Daniel Hollarek',
    description='Substitute HTML, JS and CSS with pure Python',
)