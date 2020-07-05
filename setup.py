"""Setup script for the Health Helper application."""

import os.path
from setuptools import setup

# Directory containing this file
file_dir = os.path.abspath(os.path.dirname(__file__))

# Contents of README
with open(os.path.join(file_dir, "README.md")) as f:
      README = f.read()

setup(name='Health Helper',
      version='1.0.0',
      description='Application for tracking diet and grocery spending',
      long_description=README,
      long_description_content_type="text/markdown",
      url='http://github.com/Floyd-Droid/HealthHelper',
      author='Jourdon Floyd',
      author_email='jourdonfloyd@gmail.com',
      license='MIT',
      packages=['healthhelper'],
      install_requires=['PyQt5'],
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
      ],
      entry_points={'console_scripts': 'healthhelper=healthhelper.__main__:main'}
      )
