from setuptools import setup, find_packages

setup(
    name='odnoklassniki-crawler',
    version='0.0.1',
    packages=find_packages(),
    url='',
    license='Apache 2.0',
    author='user',
    author_email='',
    description='Crawler for ok.ru', install_requires=['odnoklassniki', 'requests', 'beautifulsoup4']
)
