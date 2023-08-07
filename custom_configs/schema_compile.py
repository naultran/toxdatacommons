# -*- coding: utf-8 -*-
"""
 Created on Sat Nov  5 14:43:50 2022

 @author: Rance Nault
 """

 #import dictionaryutils

from dictionaryutils import dump_schemas_from_dir
import json

#import dictionaryutils
schema = dump_schemas_from_dir(directory="./gdcdictionary/schemas/tox_model")
schema["_settings.yaml"]["_dict_version"] = "0.1"

with open('./custom_configs/schema.json', 'w') as json_file:
    json.dump(schema, json_file)

