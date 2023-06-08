from setuptools import setup
from io import open


def load_requirements(file_list=None):
    if file_list is None:
        file_list = ['requirements.txt']
    if isinstance(file_list,str):
        file_list = [file_list]
    requirements = []
    for file in file_list:
        with open(file, encoding="utf-8-sig") as f:
            requirements.extend(f.readlines())
    return requirements


# def readme():
#     with open('doc/doc_en/whl_en.md', encoding="utf-8-sig") as f:
#         README = f.read()
#     return README


setup(
    name='table_detection',
    packages=['table_detection'],
    package_dir={'table_detection': ''},
    include_package_data=True,
    entry_points={"console_scripts": ["paddleocr= paddleocr.paddleocr:main"]},
    version='1.0.0',
    install_requires=load_requirements(['requirements.txt', 'ppstructure/requirements.txt']),
    license='Apache License 2.0',
    description='Detecting a table from pdf to xml',
    # long_description=readme(),
    # long_description_content_type='text/markdown',
    # url='https://github.com/PaddlePaddle/PaddleOCR',
    # download_url='https://github.com/PaddlePaddle/PaddleOCR.git',
    keywords=[
        'table tabledetection pdf2xml pdf2csv detection'
    ],
    classifiers=[
        'Intended Audience :: Developers', 'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7', 'Topic :: Utilities'
    ], )