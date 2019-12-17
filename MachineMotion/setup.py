#!/usr/bin/env python



from distutils.core import setup

setup(name='MachineMotion',
      version='2.2',
      description='Python API For Vention MachineMotion',
      author='Vention',
      url='https://github.com/VentionCo/mm-python-api',
    
      package_dir={'MachineMotion', ' '},
      packages = ['MachineMotion'],

      install_requires=['pathlib', 'socketIO_client','paho'],
      python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
     )

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#install-requires
# https://dzone.com/articles/executable-package-pip-install
# https://docs.python.org/3/distutils/examples.html
# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder