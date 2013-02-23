'''
Created on 22 february 2013

@author: franck
'''
__date__ ="$22 feb. 2013 08:57:29$"
__version__ = "0.2.0"
__author__ = "Valentin 'esc' Haenel <valentin.haenel@gmx.de> - Franck Roudet"

from setuptools import setup,find_packages

setup (
  name = 'pykarotz',
  version = '0.2',
  #packages = find_packages('.', exclude=["*.tests", "*.tests.*", "tests.*", "testsrc"]),
  py_modules = ['karotz'],
  # Declare your packages' dependencies here, for eg:                                                                        
  install_requires=open('requirements.txt').read(),                                                                                        
                                                                                                                             
  # Fill in these to make your Egg ready for upload to                                                                       
  # PyPI                                                                                                                     
  author = __author__ ,                                                                                                          
  author_email = '',                                                                                                         
                                                                                                                             
  description = 'karotz python API',                                                               
  url = '',                                                                                                                  
  license = 'MIT License',                                                                                                              
  long_description=open('../README.rst').read(),
  package_data = {
        # include any *.conf 

    },

# install the  executable
  entry_points={
    'console_scripts': [
    ]
  },                                                                                                                             
  # could also include long_description, download_url, classifiers, etc.                                                     
  classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],                                                                                                                           
                                                                                                                             
)