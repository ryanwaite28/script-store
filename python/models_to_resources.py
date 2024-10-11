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
  
def format_updates_from_dto(f: str) -> str:
  '''
  f: str - a converted field name string from a sequelize model definition
  return example:
  
  name: dto.name,
  '''
  
  formatted = f"{f}: dto.{f},"
    
  # print ('formatted:')
  # print (formatted)

  return formatted


def format_dto_fields(f: str) -> str:
  decorated = (
    '  ' + ('@IsOptional()' if ('| null' in f) else '@IsNotEmpty()') + '\n' + 
    '  ' + ('@IsString()' if ('string' in f) else '@IsBoolean()' if ('boolean' in f) else '@IsInt()' if ('number' in f) else '') + '\n' +
    f
  )
    
  # print ('decorated:')
  # print (decorated)

  return decorated

  
  
  
user_owner_field_by_model = {}

field_names_by_model: dict[list[str]] = {}
field_definitions_by_model: dict[list[str]] = {}
  
  
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
import {{
  {model_name}Exists,
  AuthUserOwns{model_name}
}} from './{kebob_name_plural}.guard';
import {{ Create{model_name}Dto }} from "./dto/{kebob_name_plural}.create.dto";
import {{ Update{model_name}Dto }} from "./dto/{kebob_name_plural}.update.dto";
import {{ JwtAuthorized }} from '../../middlewares/jwt.middleware';
import {{ JwtUser }} from '../../decorators/jwt.decorator';
import {{ MapType, UserEntity }} from '@app/shared';
import {{ FileUpload, FileUploadByName }} from '../../decorators/file-upload.decorator';
import {{ UploadedFile }} from 'express-fileupload';
import {{ Service }} from 'typedi';



@Controller('/web/{kebob_name_plural}')
@Controller('/mobile/{kebob_name_plural}')
@Controller('/api/{kebob_name_plural}')
@Service()
export class {model_name}Controller {{
  
  constructor(private {model_var_name}Service: {model_name}Service) {{}}

  @Get('/:id')
  getOne(@Param('id') id: number) {{
    return this.{model_var_name}Service.get{model_name}ById(id);
  }}

  @Post('')
  @UseBefore(JwtAuthorized)
  create{model_name}(
    @JwtUser() user: UserEntity,
    @Body({{ validate: true }}) dto: Create{model_name}Dto,
    @FileUpload() files: MapType<UploadedFile>
  ) {{
    return this.{model_var_name}Service.create{model_name}(user.id, dto, files);
  }}

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  update{model_name}(
    @JwtUser() user: UserEntity,
    @Param('id') id: number,
    @Body({{ validate: true }}) dto: Update{model_name}Dto
  ) {{
    return this.{model_var_name}Service.update{model_name}(user.id, id, dto);
  }}

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  patch{model_name}(
    @JwtUser() user: UserEntity,
    @Param('id') id: number,
    @Body({{ validate: true }}) dto: Update{model_name}Dto
  ) {{
    return this.{model_var_name}Service.patch{model_name}(user.id, id, dto);
  }}

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  delete{model_name}(
    @JwtUser() user: UserEntity,
    @Param('id') id: number
  ) {{
    return this.{model_var_name}Service.delete{model_name}(user.id, id);
  }}
        
}}''')
    
    
  with open(Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.guard.ts"), 'w') as f:
    f.write(f'''\
import {{ NextFunction, Request, Response }} from 'express';
import {{
  HttpStatusCodes,
  {model_name}Entity,
}} from '@app/shared';
import {{ {model_name_plural}Repo }} from "./{kebob_name_plural}.repository";



export async function {model_name}Exists(
  request: Request,
  response: Response,
  next: NextFunction
) {{
  const id = parseInt(request.params.id, 10);
  const {model_var_name}: {model_name}Entity = await {model_name_plural}Repo.findOne({{ where: {{ id }} }});
  if (!{model_var_name}) {{
    return response.status(HttpStatusCodes.NOT_FOUND).json({{
      message: `{model_name} does not exist by id: ${{ id }}`
    }});
  }}
  response.locals.{model_var_name} = {model_var_name};
  return next();
}}

export async function AuthUserOwns{model_name}(
  request: Request,
  response: Response,
  next: NextFunction
) {{
  /* TODO: implement user ownership check 
  const {model_var_name} = response.locals.{model_var_name} as {model_name}Entity;
  const isOwner = {model_var_name}.{user_owner_field_by_model.get(model_name, 'owner_id')} === request['auth'].id;
  if (!isOwner) {{
    return response.status(HttpStatusCodes.FORBIDDEN).json({{
      message: `User is not owner of {model_name} by id: ${{ {model_var_name}.id }}`
    }});
  }}
  return next();
  */
}}



''')
    
    
    
  with open(Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.service.ts"), 'w') as f:
    f.write(f'''\
import 'reflect-metadata';
import {{
  HttpStatusCodes,
  UserEntity,
  {model_name}Entity,
  MapType,
}} from "@app/shared";
import {{ Create{model_name}Dto }} from "./dto/{kebob_name_plural}.create.dto";
import {{ Update{model_name}Dto }} from "./dto/{kebob_name_plural}.update.dto";
import {{ HttpRequestException, LOGGER, AppEnvironment }} from "@app/backend";
import {{ UploadedFile }} from "express-fileupload";
import {{ AwsS3Service, AwsS3UploadResults }} from "../../services/s3.aws.service";
import {{ s3_objects_repo }} from "../s3-objects/s3-objects.repository";
import {{ ModelTypes }} from "../../lib/constants/model-types.enum";
import {{
  S3Objects,
  createTransaction
}} from '@app/backend';
import {{ Includeable, col, literal }} from "sequelize";
import {{ {model_name_plural}Repo }} from "./{kebob_name_plural}.repository";
import {{ Service }} from 'typedi';


export interface I{model_name}Service {{
  get{model_name}ById({snake_name}_id: number): Promise<{model_name}Entity>;
  create{model_name}(user_id: number, dto: Create{model_name}Dto, files?: MapType<UploadedFile>): Promise<{model_name}Entity>;
  update{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto): Promise<{{ rows: number }}>;
  patch{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto): Promise<{{ rows: number }}>;
  delete{model_name}(user_id: number, {snake_name}_id: number): Promise<{{ rows: number }}>;
}}


@Service()
export class {model_name}Service implements I{model_name}Service {{
  
  constructor() {{}}

  async get{model_name}ById({snake_name}_id: number) {{
    return {model_name_plural}Repo.findOne({{
      where: {{ id: {snake_name}_id }}
    }});
  }}
  
  async create{model_name}(user_id: number, dto: Create{model_name}Dto, files?: MapType<UploadedFile>) {{
    const s3Uploads: AwsS3UploadResults[] = [];
    let new_{snake_name}_id: number = null;
    
    try {{
      // start a new database transaction
      await createTransaction(async (transaction) => {{
        
        // create the {model_name} record
        const new_{snake_name} = await {model_name_plural}Repo.create({{
          {'\n          '.join([ (format_updates_from_dto(f)) for f in field_names_by_model.get(model_name, []) ])}
        }}, {{ transaction }});
        
        new_{snake_name}_id = new_{snake_name}.id;
        
        if (files) {{
          const media_key = 'media';
          
          if (files[media_key]) {{
            const file: UploadedFile = files[media_key];
            const s3UploadResults: AwsS3UploadResults = await AwsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await s3_objects_repo.create({{
              model_type: ModelTypes.{snake_name.upper()},
              model_id: new_{snake_name}.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }}, {{ transaction }});

            await {model_name_plural}Repo.update({{ media_id: s3Object.id }}, {{ where: {{ id: new_{snake_name}.id }}, transaction }});
          }}
        }}
        
      }});
      
      return {model_name_plural}Repo.findOne({{
        where: {{ id: new_{snake_name}_id }}
      }});
    }}
    catch (error) {{
      // transaction rollback; delete all uploaded s3 objects
      if (s3Uploads.length > 0) {{
        for (const s3Upload of s3Uploads) {{
          AwsS3Service.deleteObject(s3Upload)
          .catch((error) => {{
            LOGGER.error('s3 delete object error', {{ error, s3Upload }});
          }});
        }}
      }}

      LOGGER.error('Error creating {model_name}', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {{
        message: 'Could not create {model_name}',
        context: error
      }});
    }}
    
  }}
  
  async update{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto) {{
    const updates = await {model_name_plural}Repo.update({{
      {'\n      '.join([ (format_updates_from_dto(f)) for f in field_names_by_model.get(model_name, []) ])}
    }}, {{
      where: {{
        id: {snake_name}_id,
        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id
      }}
    }});
    return {{ rows: updates.rows }};
  }}
  
  async patch{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto) {{
    const updateData = {{ ...dto }};
    Object.keys(updateData).forEach((key) => {{
      const isEmpty = (updateData[key] === null || updateData[key] === undefined);
      if (isEmpty) {{
        delete updateData[key]
      }}
    }});
    const updates = await {model_name_plural}Repo.update(updateData, {{
      where: {{
        id: {snake_name}_id,
        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id
      }}
    }});
    return {{ rows: updates.rows }};
  }}
  
  async delete{model_name}(user_id: number, {snake_name}_id: number) {{
    const deletes = await {model_name_plural}Repo.destroy({{ 
      where: {{
        id: {snake_name}_id,
        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id
      }}
    }});
    return {{ rows: deletes.results }};
  }}
        
}}''')
    
  with open(Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.repository.ts"), 'w') as f:
    f.write(f'''\
import 'reflect-metadata';
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{ sequelize_model_class_crud_to_entity_object }} from "../../lib/utils/sequelize.utils";
import {{ {model_name_plural} }} from '@app/backend';


export const {model_name_plural}Repo = sequelize_model_class_crud_to_entity_object<{model_name}Entity>({model_name_plural});
        
''')
    
    
  with open(Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.create.dto.ts"), 'w') as f:
    f.write(f'''\
import {{
  {model_name}Entity,
}} from "@app/shared";
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


export class Create{model_name}Dto implements Partial<{model_name}Entity> {{
  
{'\n'.join([ format_dto_fields(f) for f in field_definitions_by_model.get(model_name, []) ])}
}}

        
''')
    
    
  with open(Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.update.dto.ts"), 'w') as f:
    f.write(f'''\
import {{
  {model_name}Entity,
}} from "@app/shared";
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


export class Update{model_name}Dto implements Partial<{model_name}Entity> {{
  
{'\n'.join([ format_dto_fields(f) for f in field_definitions_by_model.get(model_name, []) ])}
}}

        
''')
    
  
  
  



def convert_model_to_interface(
  models_file_path: str,
  interfaces_file_path: str = None,
  model_types_file_path: str = None,
):
  
  global user_owner_field_by_model
  global field_definitions_by_model
  global field_names_by_model
  
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
      field_owner_match = re.search("references: { model: Users, key: 'id' }", use_line)
      if (field_name_match and not (field_name_match.group(1) == "id")) and field_type_match and field_type_def_match and is_in_interface:
        
        field_not_nullable_match = re.search("(allowNull: false)", use_line)
      
        use_name = field_name_match.group(1)
        use_type = \
          "string" if (field_type_match and field_type_match.group(1) in ["STRING", "TEXT", "JSON", "UUID", "UUIDV4", "DATE", "DATETIME"]) \
          else "number" if (field_type_match and field_type_match.group(1) in ["INTEGER", "BIGINT", "DECIMAL", "FLOAT", "REAL"]) \
          else "boolean" if (field_type_match and field_type_match.group(1) in ["BOOLEAN"]) else "boolean"
        
        if not field_not_nullable_match:
          use_type += " | null"
          
        field_definition = f'''  {use_name}: {use_type};\n'''  
        new_file_contents.append(field_definition)
        
        field_definitions_by_model[model_name] = field_definitions_by_model.get(model_name, [])
        field_definitions_by_model[model_name].append(field_definition)
        
        field_names_by_model[model_name] = field_names_by_model.get(model_name, [])
        field_names_by_model[model_name].append(use_name)
        
        if field_owner_match:
          user_owner_field_by_model[model_name] = use_name
        
        continue
        
      if ('});' in use_line) and is_in_interface:
        new_file_contents.append('}\n\n')
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
  
  model_types_contents = [
    'export enum ModelTypes {\n',
  ]
  try:
    for model_name in singular_model_names:
      snake_name = camel_to_snake(model_name)
      model_types_contents.append(f'  {snake_name.upper()} = "{snake_name.upper()}",\n')
    model_types_contents.append('}\n')
      
    with open(f"model-types-converted.enum.ts", 'w') as f:
      f.write(''.join(model_types_contents))
    
    if model_types_file_path:
      with open(model_types_file_path, 'w') as f:
        f.write(''.join(model_types_contents))
  except Exception as e:
    print(f"Error writing to interfaces file: {e}")
    pass
  
  
  print(field_definitions_by_model)
    
  
  
  return singular_model_names
  
  

  
  
def run():
  
  use_models_file_path = "src/libs/backend/src/lib/app.database.ts"
  
  use_interfaces_file_path = "src/libs/shared/src/lib/interfaces/models.interface.ts"
  
  use_model_types_file_path = "src/apps/app-server/src/lib/constants/model-types.enum.ts"
  
  # --- #
  
  singular_model_names = convert_model_to_interface(
    models_file_path = use_models_file_path,
    interfaces_file_path = use_interfaces_file_path,
    model_types_file_path = use_model_types_file_path,
  )
  
  print('singular_model_names:', singular_model_names)
  
  resources_base_path = "src/apps/app-server/src/resources"
  
  for model_name in singular_model_names:
    create_resource(model_name = model_name, resources_base_path = resources_base_path)
  
  
run()
print("Finished!")
