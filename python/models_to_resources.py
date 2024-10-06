import os, sys, re
from pathlib import Path



def camel_to_kebab(s):
    """Converts a camelCase string to kebab-case."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s).lower()
    return s
  
def camel_to_snake(s):
    """Converts a camelCase string to snake-case."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()
    return s
  
def pluralize(s: str) -> str:
  """Pluralizes a singular noun."""
  if s.endswith('s'):
    return s + 'es'
  elif s.endswith('ey'):
    return s + 's'
  elif s.endswith('y'):
    return s[:-1] + 'ies'
  else:
    return s + 's'
  
  
  
  
def create_resource(
  model_name: str,
  resources_base_path: str
):
    
  kebob_name = camel_to_kebab(model_name)
  snake_name = camel_to_snake(model_name)
  
  model_name_plural = pluralize(model_name)
  model_var_name = model_name[0].lower() + model_name[1:]
  
  singular = model_name.lower()
  plural = (singular[:-1] + 'ies') if (singular[-1] == 'y') else (singular + 's')
  
  kebob_name_plural = pluralize(kebob_name)
  snake_name_plural = pluralize(snake_name)
  
  singular_caps = singular.capitalize()
  plural_caps = plural.capitalize()
  
  # print('names: ', {
  #   "model_name": model_name,
  #   "kebob_name": kebob_name,
  #   "kebob_name_plural": kebob_name_plural,
  #   "snake_name": snake_name,
  #   "snake_name_plural": snake_name_plural,
  #   "model_name_plural": model_name_plural,
  #   "model_var_name": model_var_name,
  #   "singular": singular,
  #   "plural": plural,
  #   "singular_caps": singular_caps,
  #   "plural_caps": plural_caps,
  # })

  # base_path = f"src/apps/app-server/src/resources{plural}"
  base_path = resources_base_path



  if os.path.exists(base_path + f"/{kebob_name_plural}"):
    # print(f"Resource \"{model_name}\" already exists/created; exiting...")
    return


  Path(f"{base_path}/{kebob_name_plural}").mkdir(parents = True, exist_ok = True)
  Path(f"{base_path}/{kebob_name_plural}/dto").mkdir(parents = True, exist_ok = True)
  Path(f"{base_path}/{kebob_name_plural}/dto/validations").mkdir(parents = True, exist_ok = True)
  
  
  
  with open(Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.controller.ts"), 'w') as f:
    f.write(f'''\
import 'reflect-metadata';
import {{
  Controller,
  Param,
  Body,
  Get,
  Post,
  Put,
  Delete,
  UseBefore,
  Patch
}} from 'routing-controllers';

import {{ {model_name}Service }} from './{kebob_name_plural}.service';
import {{ Create{model_name}Dto }} from "./dto/{kebob_name_plural}.create.dto";
import {{ Update{model_name}Dto }} from "./dto/{kebob_name_plural}.update.dto";
import {{ JwtUserAuthorized }} from '../../middlewares/jwt.middleware';
import {{ JwtUser }} from '../../decorators/jwt.decorator';
import {{ UserEntity }} from '@app/shared';
import {{ FileUpload, FileUploadByName }} from '../../decorators/file-upload.decorator';
import {{ UploadedFile }} from 'express-fileupload';



@Controller('/web/{kebob_name_plural}')
@Controller('/mobile/{kebob_name_plural}')
@Controller('/api/{kebob_name_plural}')
export class {model_name}Controller {{

  @Get('/:id')
  getOne(@Param('id') id: number) {{
    return {model_name}Service.get{model_name}ById(id);
  }}

  @Post('')
  @UseBefore(JwtUserAuthorized)
  signup(@JwtUser() user: UserEntity, @Body({{ validate: true }}) dto: Create{model_name}Dto) {{
    return {model_name}Service.create{model_name}(user.id, dto);
  }}

  @Put('/:id')
  @UseBefore(JwtUserAuthorized)
  put(@JwtUser() user: UserEntity, @Param('id') id: number, @Body({{ validate: true }}) dto: Update{model_name}Dto) {{
    return {model_name}Service.update{model_name}(user.id, id, dto);
  }}

  @Patch('/:id')
  @UseBefore(JwtUserAuthorized)
  patch(@JwtUser() user: UserEntity, @Param('id') id: number, @Body({{ validate: true }}) dto: Update{model_name}Dto) {{
    return {model_name}Service.patch{model_name}(user.id, id, dto);
  }}

  @Delete('/:id')
  @UseBefore(JwtUserAuthorized)
  delete(@JwtUser() user: UserEntity, @Param('id') id: number) {{
    return {model_name}Service.delete{model_name}(user.id, id);
  }}
        
}}''')
    
    
  with open(Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.service.ts"), 'w') as f:
    f.write(f'''\
import 'reflect-metadata';
import {{
  HttpStatusCodes,
  UserEntity,
}} from "@app/shared";
import {{ Create{model_name}Dto }} from "./dto/{kebob_name_plural}.create.dto";
import {{ Update{model_name}Dto }} from "./dto/{kebob_name_plural}.update.dto";
import {{ HttpRequestException, LOGGER, AppEnvironment }} from "@app/backend";
import {{ UploadedFile }} from "express-fileupload";
import {{ AwsS3Service, AwsS3UploadResults }} from "../../services/s3.aws.service";
import {{ s3_objects_repo }} from "../s3-objects/s3-objects.repository";
import {{ ModelTypes }} from "../../lib/constants/model-types.enum";
import {{ readFile }} from "fs/promises";
import {{ S3Objects }} from "../../app.database";
import {{ Includeable, col, literal }} from "sequelize";
import {{ {snake_name_plural}_repo }} from "./{kebob_name_plural}.repository";



export class {model_name}Service {{

  static async get{model_name}ById({snake_name}_id: number) {{
    return {snake_name_plural}_repo.findOne({{
      where: {{ id: {snake_name}_id }}
    }});
  }}
  
  static async create{model_name}(user_id: number, dto: Create{model_name}Dto) {{
    
  }}
  
  static async update{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto) {{
    
  }}
  
  static async patch{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto) {{
    
  }}
  
  static async delete{model_name}(user_id: number, {snake_name}_id: number) {{
    
  }}
        
}}''')
    
  with open(Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.repository.ts"), 'w') as f:
    f.write(f'''\
import 'reflect-metadata';
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{ sequelize_model_class_crud_to_entity_object }} from "../../lib/utils/sequelize.utils";
import {{ {model_name_plural} }} from "../../app.database";


export const {snake_name_plural}_repo = sequelize_model_class_crud_to_entity_object<{model_name}Entity>({model_name_plural});
        
''')
    
    
  with open(Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.create.dto.ts"), 'w') as f:
    f.write(f'''\
import {{
  IsBoolean,
  IsEmail,
  IsIn,
  IsNotEmpty,
  IsOptional,
  IsString,
  IsNumber,
  IsInt,
  Matches,
  ValidateIf,
}} from 'class-validator';


export class Create{model_name}Dto {{
  
  

}}

        
''')
    
    
  with open(Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.update.dto.ts"), 'w') as f:
    f.write(f'''\
import {{
  IsBoolean,
  IsEmail,
  IsIn,
  IsNotEmpty,
  IsOptional,
  IsString,
  IsNumber,
  IsInt,
  Matches,
  ValidateIf,
}} from 'class-validator';


export class Update{model_name}Dto {{
  
  

}}

        
''')
    
  
  
  



def convert_model_to_interface(
  models_file_path: str,
  interfaces_file_path: str = None
):
  
  # file with sequelize models
  
  singular_model_names: list[str] = []
  
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
          
        singular_model_names.append(model_name)
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
    
  try:
    if interfaces_file_path:
      with open(interfaces_file_path, 'w') as f:
        f.write(joined_contents)
  except Exception as e:
    print(f"Error writing to interfaces file: {e}")
    pass
    
  
  
  return singular_model_names
  
  
  
  
  
def run():
  
  use_models_file_path = "src/apps/app-server/src/app.database.ts"
  
  use_interfaces_file_path = "src/libs/shared/src/lib/interfaces/models.interface.ts"
  
  # --- #
  
  singular_model_names = convert_model_to_interface(
    models_file_path = use_models_file_path,
    interfaces_file_path = use_interfaces_file_path
  )
  
  print('singular_model_names:', singular_model_names)
  
  resources_base_path = "src/apps/app-server/src/resources"
  
  for model_name in singular_model_names:
    create_resource(model_name = model_name, resources_base_path = resources_base_path)
  
  
run()
print("Finished!")