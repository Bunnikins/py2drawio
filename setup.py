from setuptools import setup

setup(name='py2drawio',
    version='0.1',
    description='Define a draw.io diagram using python',
    url='https://github.com/Bunnikins/py2drawio',
    author='Bunnikins',
    author_email='bunnikins@bunnicloud.com',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pyyaml',
    ],
    python_requires='>=3.6',
)