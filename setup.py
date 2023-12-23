from setuptools import setup

setup(
    name="clean_folder",
    version='0.0.1',
    description='Console script for sort files in target folder',
    url='https://github.com/oryabinsky/goit_python_core_homework_7',
    author='Mike Oryabinsky',
    author_email='mike.oryabinsky@gmail.com',
    license='MIT',
    packages=['clean_folder'],
    entry_points={
        'console_scripts': ['clean-folder = clean_folder.clean:main']
    }
)