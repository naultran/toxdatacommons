"""
This script dumps all schema files in currently installed gdcdictionary
to one json schema to ./artifacts folder.

"""
import json
import os
import sys

#from gdcdictionary import SCHEMA_DIR
from dictionaryutils import dump_schemas_from_dir

SCHEMA_DIR="./schemas"
print(SCHEMA_DIR)

if len(sys.argv) > 1 :
   print('hello')
   print(sys.argv[1])
   with open(os.path.join("../custom_configs", "schema.json"), "w") as f:
       print(SCHEMA_DIR)
       json.dump(dump_schemas_from_dir(SCHEMA_DIR), f)
else:
    with open(os.path.join("../custom_configs", "schema.json"), "w") as f:
        json.dump(dump_schemas_from_dir(SCHEMA_DIR), f)

