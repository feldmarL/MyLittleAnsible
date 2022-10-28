from setuptools import setup, find_packages

setup(
    name='my_little_ansible',
    version='0.0.1',
    url='',
    license='',
    author='louis.feldmar',
    author_email='',
    description='',
    package_dir={"": "src"},
    packages=find_packages(
        where='src',
        include=['*'],
    ),
    entry_points = {
        'console_scripts': [
            'mla = my_little_ansible:cmd_interpreter',
        ]
    }
)