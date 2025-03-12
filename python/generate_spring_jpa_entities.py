import re, os, shutil

def singularize_word(word):
    """
    Returns the singular form of a word, if possible.
    It handles some common pluralization rules, but is not exhaustive.
    """
    # List of common exceptions that don't follow regular pluralization rules
    exceptions = {
        'people': 'person',
        'men': 'man',
        'children': 'child',
        'teeth': 'tooth',
        'feet': 'foot',
        'mice': 'mouse',
        'geese': 'goose',
        'wolves': 'wolf',
        'lives': 'life',
        'knives': 'knife',
        'wives': 'wife',
        'leaves': 'leaf',
        'shelves': 'shelf',
        'halves': 'half',
        'quizzes': 'quiz',
        'profiles': 'profile',
        'phones': 'phone',
    }
    
    word_lower = word.lower()
    
    for exception in exceptions:
        if word_lower.endswith(exception):
            return word[:-len(exception)] + exceptions[exception]
          
    # if word_lower in exceptions:
    #     return exceptions[word_lower]
    
    # Rules for handling common plural endings
    if word.endswith('ies'):
        return re.sub(r'ies$', 'y', word)
    # elif word.endswith('es'):
    #     return re.sub(r'es$', '', word)
    elif word.endswith('s') and not word.endswith('ss'):
        return re.sub(r's$', '', word)
    else:
        return word # If no rule applies, return the original word

def make_class_name(table_name, singularize = True):
  table_name_split = (table_name.split('.')[-1]).split('_')
  # print("[make_class_name] before", table_name_split)
  if singularize:
    table_name_split[-1] = singularize_word(table_name_split[-1])
  # print("[make_class_name] after", table_name_split)
  class_name = ''.join(word.capitalize() for word in table_name_split)
  return snake_to_camel(class_name)

def sql_to_java_type(sql_type):
    if 'UUID' in sql_type:
        return 'UUID'
    if 'INT' in sql_type:
        return 'Integer'
    if 'BIGINT' in sql_type:
        return 'BigInteger'
    if 'BOOLEAN' in sql_type:
        return 'Boolean'
    elif ('VARCHAR' in sql_type or 'TEXT' in sql_type or 'JSON' in sql_type or 'JSOB' in sql_type):
        return 'String'
    elif 'DATE' in sql_type or 'TIMESTAMP' in sql_type:
        return 'LocalDateTime'
    elif 'DOUBLE' in sql_type or 'DECIMAL' in sql_type:
        return 'Double'
    else:
        return 'Object'


def generate_service_interface(table_name, package_prefix):
    class_name = make_class_name(table_name)
    
    return f"""\
package {package_prefix}.services.interfaces;

public interface {class_name}Service {{
  
  
  
}}
"""


def generate_service_interface_implementation(table_name, package_prefix):
    class_name = make_class_name(table_name)
    var_name = class_name[0].lower() + class_name[1:]
    
    return f"""\
package {package_prefix}.services.implementations;

import {package_prefix}.services.interfaces.{class_name}Service;
import {package_prefix}.entities.{class_name}Entity;
import {package_prefix}.dto.{class_name}Dto;
import {package_prefix}.repositories.{class_name}Repository;
import org.springframework.stereotype.Service;

@Service
public class {class_name}ServiceImpl implements {class_name}Service {{
 
    private final {class_name}Repository {var_name}Repository;
    
    public {class_name}ServiceImpl(
        {class_name}Repository {var_name}Repository
    ) {{
        this.{var_name}Repository = {var_name}Repository;
    }} 
  
}}
"""




def generate_main_service_interface(service_name, package_prefix):
    class_name = make_class_name(service_name, False)
    
    return f"""\
package {package_prefix}.services.interfaces;

public interface {class_name}Service {{
  
  
  
}}
"""


def generate_main_service_interface_implementation(service_name, package_prefix, import_configs, datasources_package_prefix):
# {'\n'.join([ import_config['import_stmts'] for import_config in import_configs])}
    class_name = make_class_name(service_name, False)
    
    return f"""\
package {package_prefix}.services.implementations;

import org.springframework.stereotype.Service;
import {package_prefix}.services.interfaces.{class_name}Service;
import {datasources_package_prefix}.entities.*;
import {datasources_package_prefix}.dto.*;
import {datasources_package_prefix}.repositories.*;

@Service
public class {class_name}ServiceImpl implements {class_name}Service {{
 
{'\n'.join([ f"    private final {import_config['model_name']}Repository {import_config['model_name'][0].lower() + import_config['model_name'][1:]}Repository;" for import_config in import_configs])}
    
    public {class_name}ServiceImpl(
{',\n'.join([ f"        {import_config['model_name']}Repository {import_config['model_name'][0].lower() + import_config['model_name'][1:]}Repository" for import_config in import_configs])}
    ) {{
{'\n'.join([ f"        this.{import_config['model_name'][0].lower() + import_config['model_name'][1:]}Repository = {import_config['model_name'][0].lower() + import_config['model_name'][1:]}Repository;" for import_config in import_configs])}
    }} 
  
}}
"""





def generate_dto(table_name, columns, package_prefix):
    class_name = make_class_name(table_name)
    
    fields = []
    getters = []
    
    for col_name, data_type in columns.items():
        java_type = sql_to_java_type(data_type)
        fields.append(f"    private {"String" if (java_type == 'UUID') else f"String" if ("JSON" in data_type) else java_type} {snake_to_camel(col_name)};")
        getters.append(f"            entity.get{snake_to_camel(col_name.capitalize())}(){".toString()" if (java_type == 'UUID') else ""}")
    
    return f"""\
package {package_prefix}.dto;

import {package_prefix}.entities.{class_name}Entity;
import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class {class_name}Dto {{

{"\n".join(fields)}

    public static {class_name}Dto fromEntity({class_name}Entity entity) {{
        return new {class_name}Dto(
{',\n'.join(getters)}
        );
    }}
    
    public static {class_name}Entity toEntity({class_name}Dto dto) {{
        return {class_name}Entity.builder()
{'\n'.join([f"            .{snake_to_camel(col_name)}({ "UUID.fromString(" if sql_to_java_type(data_type) == "UUID" else "" }dto.get{snake_to_camel(col_name.capitalize())}(){ ")" if sql_to_java_type(data_type) == "UUID" else "" })" for col_name, data_type in columns.items()])}
            .build();
    }}

}}
"""

def generate_repository(table_name, columns, package_prefix):
    class_name = make_class_name(table_name)

    return f"""\
package {package_prefix}.repositories;

import {package_prefix}.entities.{class_name}Entity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface {class_name}Repository extends JpaRepository<{class_name}Entity, UUID> {{}}

"""

def generate_service_controller(service_name, package_prefix):
    class_name = make_class_name(service_name, False)

    return f"""\
package {package_prefix}.controllers;

import {package_prefix}.services.interfaces.{class_name}Service;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.util.UUID;



@RestController
@RequestMapping("/{service_name}")
public class {class_name}Controller {{

    private final {class_name}Service {service_name}Service;
    
    public {class_name}Controller(
      {class_name}Service {service_name}Service
    ) {{
        this.{service_name}Service = {service_name}Service;
    }}

}}

"""

def generate_main_service_import_config(table_name, package_prefix):
    class_name = make_class_name(table_name)
    
    import_entity = f"import {package_prefix}.entities.{class_name}Entity;"
    import_dto = f"import {package_prefix}.dto.{class_name}Dto;"
    import_repo = f"import {package_prefix}.repositories.{class_name}Repository;"
    
    import_stmts = f"""\
{import_entity}
{import_dto}
{import_repo}"""

    return {
      "model_name": f"{class_name}",
      "import_entity": import_entity,
      "import_dto": import_dto,
      "import_repo": import_repo,
      "import_stmts": import_stmts,
    }
    
    
def snake_to_camel(snake_string):
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
  
def generate_entity_class(table_name, columns, package_prefix):
    class_name = make_class_name(table_name)
    entity_code = f"""\
package {package_prefix}.entities;

import jakarta.persistence.*;
import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.ColumnTransformer;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcType;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import org.hibernate.type.descriptor.jdbc.UUIDJdbcType;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "{table_name}")
public class {class_name}Entity {{
"""
    for col_name, col_type in columns.items():
        java_type = sql_to_java_type(col_type)
        entity_code += f"""
    {"""@Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @JdbcType(UUIDJdbcType.class)""" 
    if ("UUID" in col_type and col_name == "id") 
    else """
    @JdbcTypeCode(SqlTypes.JSON)
    @ColumnTransformer(write = "?::jsonb")"""
    if ("JSON" in col_type)
    else ""}
    @Column(name = "{col_name}")
    private {java_type} {snake_to_camel(col_name)};"""
#     entity_code += """
#     // Getters and setters
# """
#     for col_name, col_type in columns.items():
#         java_type = sql_to_java_type(col_type)
#         entity_code += f"""
#     public {java_type} get{col_name.capitalize()}() {{
#         return {col_name};
#     }}

#     public void set{col_name.capitalize()}({java_type} {col_name}) {{
#         this.{col_name} = {col_name};
#     }}
# """
    entity_code += """

}
"""
    return entity_code

def parse_sql_file(sql_config):
    service_name = sql_config['service']
    sql_file_path = sql_config['sql_path']
    datasources_package_prefix = f"com.modernapps.maverick.gateway_api.datasources.{sql_config['service']}"
    app_package_prefix = f"com.modernapps.maverick.gateway_api"
  
  
    with open(sql_file_path, 'r') as sql_file:
        sql_content = sql_file.read()
    table_definitions = re.findall(r'CREATE TABLE IF NOT EXISTS `?(.*?)`? \((.*?)\);', sql_content, re.DOTALL)
    
    # print(table_definitions)
    
    entities = {}
    dto = {}
    repositories = {}
    service_interfaces = {}
    service_implementations = {}
    import_configs: list = []
    
    for table_name, columns_def in table_definitions:
        columns = {}
        for column_def in columns_def.split(','):
            column_def = column_def.strip()
            
            if column_def.startswith('PRIMARY') or column_def.startswith('CONSTRAINT') or not column_def:
                continue
            col_name_match = re.search(r'`?(\w+)`?', column_def)
            col_type_match = re.search(r'\s([A-Z].*)', column_def)
          
            match = bool(col_name_match and col_type_match)
            
            # print({
            #   "column_def": column_def,
            #   "col_name_match": col_name_match,
            #   "col_type_match": col_type_match,
            #   "match": match,
            # })
            
            if match:
                col_name = col_name_match.group(1)
                col_type = col_type_match.group(1).split(' ')[0]
                columns[col_name] = col_type
                
        entities[table_name] = generate_entity_class(table_name, columns, datasources_package_prefix)
        dto[table_name] = generate_dto(table_name, columns, datasources_package_prefix)
        repositories[table_name] = generate_repository(table_name, columns, datasources_package_prefix)
        service_interfaces[table_name] = generate_service_interface(table_name, datasources_package_prefix)
        service_implementations[table_name] = generate_service_interface_implementation(table_name, datasources_package_prefix)
        
        import_configs_by_table = generate_main_service_import_config(table_name, datasources_package_prefix)
        import_configs.append(import_configs_by_table)
        
    main_service_interface = generate_main_service_interface(service_name, app_package_prefix)
    main_service_implementation = generate_main_service_interface_implementation(service_name, app_package_prefix, import_configs, datasources_package_prefix)
    controller = generate_service_controller(service_name, app_package_prefix)

    return {
      'entities': entities,
      'dto': dto,
      'repositories': repositories,
      'service_interfaces': service_interfaces,
      'service_implementations': service_implementations,
      'main_service_interface': main_service_interface,
      'main_service_implementation': main_service_implementation,
      'controller': controller,
    }


def write_to_file(contents, path_full):
    output_dir = os.path.dirname(path_full)
    
    os.makedirs(output_dir, exist_ok=True)
    with open(path_full, 'w') as file:
      file.write(contents)
                    
def write_itema_to_files(items, classNameSuffix, output_dir):
     for table_name, code in items.items():
        class_name = make_class_name(table_name)
        file_path = os.path.join(output_dir, f"{class_name}{classNameSuffix}.java")
        write_to_file(code, file_path)
            
    #  os.makedirs(output_dir, exist_ok=True)
    #  for table_name, code in items.items():
    #     class_name = make_class_name(table_name)
    #     file_path = os.path.join(output_dir, f"{class_name}{classNameSuffix}.java")
    #     with open(file_path, 'w') as file:
    #         file.write(code)
          



if __name__ == "__main__":
    sql_configs = [
      { "service": "", "sql_path": '' }
    ]
    
    if os.path.exists("src"):
      shutil.rmtree("src")
      
    for sql_config in sql_configs:
      # print("processing: ", sql_configs)
      
      results = parse_sql_file(sql_config)
      
      write_itema_to_files(items = results['entities'], classNameSuffix = "Entity", output_dir = f'src/datasources/{sql_config['service']}/entities')
      write_itema_to_files(items = results['dto'], classNameSuffix = "Dto", output_dir = f'src/datasources/{sql_config['service']}/dto')
      write_itema_to_files(items = results['repositories'], classNameSuffix = "Repository", output_dir = f'src/datasources/{sql_config['service']}/repositories')
      write_itema_to_files(items = results['service_interfaces'], classNameSuffix = "Service", output_dir = f'src/datasources/{sql_config['service']}/services/interfaces')
      write_itema_to_files(items = results['service_implementations'], classNameSuffix = "ServiceImpl", output_dir = f'src/datasources/{sql_config['service']}/services/implementations')
      
      write_to_file(contents = results['main_service_interface'], path_full = f'src/services/interfaces/{make_class_name(sql_config['service'], False)}Service.java')
      write_to_file(contents = results['main_service_implementation'], path_full = f'src/services/implementations/{make_class_name(sql_config['service'], False)}ServiceImpl.java')
      write_to_file(contents = results['controller'], path_full = f'src/controllers/{make_class_name(sql_config['service'], False)}Controller.java')
    # END for
      
    print("Resource classes generated successfully")