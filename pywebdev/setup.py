from setuptools import setup, find_packages

setup(
    name='pywebdev',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'flask',
        'yattag'
    ],
    author='Daniel Hollarek',
    description='Substitute HTML, JS and CSS with pure Python',
)
