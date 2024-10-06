import os, sys, re
from pathlib import Path


def run():
  
  # file with sequelize models
  
  models_file_path = "src/apps/app-server/src/app.database.ts"
  models_file = Path(models_file_path)
  
  new_file_contents = [
    "import { _BaseEntity } from './base-model.interface';\n",
    "\n\n\n"
  ]
  
  if not models_file.is_file():
    print("File not found.")
    return
  
  
  with open(models_file, 'r') as f:
    
    is_in_interface = False
    
    for line in f.readlines():
      use_line = line.rstrip('\n')
      
      if ('sequelize.define' in use_line) and (not ("sequelize.define('_" in use_line)):
        line_tokens = use_line.split(' ')
        model_name = line_tokens[2].replace(":", "")
        if model_name.endswith('ies'):
          model_name = model_name[:-3] + 'y'
        elif model_name.endswith('s'):
          model_name = model_name[:-1]
          
        new_file_contents.append(f'''export interface {model_name}Entity extends _BaseEntity {{\n''')
        is_in_interface = True
        continue
      
      field_name_match = re.search("([a-zA-Z-0-9-_]+)", use_line)
      field_type_def_match = re.search("type: ", use_line)
      field_type_match = re.search("([A-Z]+)", use_line)
      if (field_name_match and not (field_name_match.group(1) == "id")) and field_type_match and field_type_def_match and is_in_interface:
        
        field_not_nullable_match = re.search("(allowNull: false)", use_line)
      
        use_name = field_name_match.group(1)
        use_type = \
          "string" if (field_type_match and field_type_match.group(1) in ["STRING", "TEXT", "JSON", "UUID", "UUIDV4", "DATE", "DATETIME"]) \
          else "number" if (field_type_match and field_type_match.group(1) in ["INTEGER", "BIGINT", "DECIMAL", "FLOAT", "REAL"]) \
          else "boolean" if (field_type_match and field_type_match.group(1) in ["BOOLEAN"]) else "boolean"
        
        if not field_not_nullable_match:
          use_type += " | null"
          
        new_file_contents.append(f'''  {use_name}: {use_type};''')
        new_file_contents.append('\n')
        continue
        
      if ('});' in use_line) and is_in_interface:
        new_file_contents.append('}')
        new_file_contents.append('\n\n')
        is_in_interface = False
        continue
        
        
  joined_contents = ''.join(new_file_contents)
  
  with open(f"model-interfaces-converted.ts", 'w') as f:
    f.write(joined_contents)
  
  
  
  
  
  
  
run()