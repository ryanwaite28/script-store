import os, sys
from pathlib import Path




def run():
  
  print('cli args:', sys.argv)

  if len(sys.argv[1:]) != 1:
    print("Incorrect args")
    return
    
  singular = sys.argv[1].lower()
  plural = (singular + 'ies') if (singular[-1] == 'y') else (singular + 's')
  
  singular_caps = singular.capitalize()
  plural_caps = plural.capitalize()
  
  print('singular: ', singular)
  print('singular_caps: ', singular_caps)
  print('plural: ', plural)
  print('plural_caps: ', plural_caps)
  
  base_path = f"src/apps/app-server/src/resources/{plural}"
  
  if os.path.exists(base_path):
    print(f"Resource \"{singular}\" already exists/created; exiting...")
    return


  Path(f"{base_path}/{plural}").mkdir(parents = True, exist_ok = True)
  Path(f"{base_path}/{plural}/dto").mkdir(parents = True, exist_ok = True)
  Path(f"{base_path}/{plural}/dto/validations").mkdir(parents = True, exist_ok = True)
  
  
  
  with open(Path(f"{base_path}/{plural}/{plural}.controller.ts"), 'w') as f:
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

import {{ {plural_caps}Service }} from './{plural}.service';
import {{ Create{singular_caps}Dto }} from "./dto/create-{singular}.dto";
import {{ Update{singular_caps}Dto }} from "./dto/update-{singular}.dto";
import {{ JwtUserAuthorized }} from '../../middlewares/jwt.middleware';
import {{ JwtUser }} from '../../decorators/jwt.decorator';
import {{ UserEntity }} from '@app/shared';
import {{ FileUpload, FileUploadByName }} from '../../decorators/file-upload.decorator';
import {{ UploadedFile }} from 'express-fileupload';



@Controller('/web/{plural}')
@Controller('/mobile/{plural}')
@Controller('/api/{plural}')
export class {plural_caps}Controller {{

  @Get('/:id')
  getOne(@Param('id') id: number) {{
    return {plural_caps}Service.get{singular_caps}ById(id);
  }}

  @Post('')
  @UseBefore(JwtUserAuthorized)
  signup(@JwtUser() user: UserEntity, @Body({{ validate: true }}) dto: Create{singular_caps}Dto) {{
    return {plural_caps}Service.create{singular_caps}(user.id, dto);
  }}

  @Put('/:id')
  @UseBefore(JwtUserAuthorized)
  put(@JwtUser() user: UserEntity, @Body({{ validate: true }}) dto: Update{singular_caps}Dto) {{
    return {plural_caps}Service.update{singular_caps}(user.id, dto);
  }}

  @Patch('/:id')
  @UseBefore(JwtUserAuthorized)
  patch(@JwtUser() user: UserEntity, @Body({{ validate: true }}) dto: Update{singular_caps}Dto) {{
    return {plural_caps}Service.patch{singular_caps}(user.id, dto);
  }}

  @Delete('/:id')
  @UseBefore(JwtUserAuthorized)
  delete(@JwtUser() user: UserEntity, @Param('id') {singular}_id: number) {{
    return {plural_caps}Service.delete{singular_caps}(user.id, {singular}_id);
  }}
        
}}''')
    
    
  with open(Path(f"{base_path}/{plural}/{plural}.service.ts"), 'w') as f:
    f.write(f'''\
import 'reflect-metadata';
import {{
  HttpStatusCodes,
  UserEntity,
}} from "@app/shared";
import {{ Create{singular_caps}Dto }} from "./dto/create-{singular}.dto";
import {{ Update{singular_caps}Dto }} from "./dto/update-{singular}.dto";
import {{ HttpRequestException, LOGGER, AppEnvironment }} from "@app/backend";
import {{ UploadedFile }} from "express-fileupload";
import {{ AwsS3Service, AwsS3UploadResults }} from "../../services/s3.aws.service";
import {{ s3objects_repo }} from "../s3objects/s3objects.repository";
import {{ ModelTypes }} from "../../lib/constants/model-types.enum";
import {{ readFile }} from "fs/promises";
import {{ S3Objects }} from "../../app.database";
import {{ Includeable, col, literal }} from "sequelize";
import {{ {plural}_repo }} from "./{plural}.repository";



export class {plural_caps}Service {{

  static async get{singular_caps}ById({singular}_id: number) {{
    return {plural}_repo.findOne({{
      where: {{ id: {singular}_id }}
    }});
  }}
  
  static async create{singular_caps}(user_id: number, dto: Create{singular_caps}Dto) {{
    
  }}
  
  static async update{singular_caps}({singular}_id: number, dto: Update{singular_caps}Dto) {{
    
  }}
  
  static async patch{singular_caps}({singular}_id: number, dto: Update{singular_caps}Dto) {{
    
  }}
  
  static async delete{singular_caps}(user_id: number, {singular}_id: number) {{
    
  }}
        
}}''')
    
  with open(Path(f"{base_path}/{plural}/{plural}.repository.ts"), 'w') as f:
    f.write(f'''\
import 'reflect-metadata';
import {{
  {singular_caps}Entity,
}} from "@app/shared";
import {{ sequelize_model_class_crud_to_entity_object }} from "../../lib/utils/sequelize.utils";
import {{ {plural_caps} }} from "../../app.database";


export const {plural}_repo = sequelize_model_class_crud_to_entity_object<{singular_caps}Entity>({plural_caps});
        
''')
    
    
  with open(Path(f"{base_path}/{plural}/dto/create-{singular}.dto.ts"), 'w') as f:
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


export class Create{singular_caps}Dto {{
  
  

}}

        
''')
    
    
  with open(Path(f"{base_path}/{plural}/dto/update-{singular}.dto.ts"), 'w') as f:
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


export class Update{singular_caps}Dto {{
  
  

}}

        
''')
    
  
  
  
  
  print('Finished')
  
  
  
  
  
  
run()