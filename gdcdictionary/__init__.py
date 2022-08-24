import os
from dictionaryutils import DataDictionary as GDCDictionary

# SCHEMA_DIR = 'use to override location to schema folder and comment assignment below'
SCHEMA_DIR = '/cygdrive/c/Users/15177/anaconda3/envs/py38/lib/site-packages/gdcdictionary/schemas/'

SCHEMA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'schemas')
print('Schemas folder location: ', SCHEMA_DIR)
gdcdictionary = GDCDictionary(root_dir=SCHEMA_DIR)

