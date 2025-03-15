# a few custom logic here and there, but mostly general purpose code
# to generate spring jpa entities from sql files
# the code is not perfect, but it's a good starting point

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
      
def sql_to_typescript_type(sql_type):
    if (
      'BIGINT' in sql_type 
      or 'INT' in sql_type 
      or 'SMALLINT' in sql_type 
      or 'SERIAL' in sql_type 
      or 'BIGSERIAL' in sql_type 
      or 'DECIMAL' in sql_type 
      or 'NUMERIC' in sql_type 
      or 'REAL' in sql_type 
      or 'DOUBLE' in sql_type 
      or 'FLOAT' in sql_type 
      or 'BIGDECIMAL' in sql_type
      or 'MONEY' in sql_type
    ):
        return 'number'
    if 'BOOLEAN' in sql_type:
        return 'boolean'
    elif ('VARCHAR' in sql_type or 'TEXT' in sql_type or 'JSON' in sql_type or 'JSOB' in sql_type or 'UUID' in sql_type or 'CHAR' in sql_type):
        return 'string'
    elif 'DATE' in sql_type or 'TIME' in sql_type:
        return 'string'
    else:
        return 'any'


def generate_service_interface(table_name, package_prefix):
    class_name = make_class_name(table_name)
    
    return f"""\
package {package_prefix}.services.interfaces;

import {package_prefix}.dto.{class_name}Dto;
import java.util.UUID;


public interface {class_name}Service {{
  
    {class_name}Dto getById(UUID id);
    
    {class_name}Dto create({class_name}Dto dto);
    
    {class_name}Dto update(UUID id, {class_name}Dto dto);
    
    {class_name}Dto patch(UUID id, {class_name}Dto dto);
    
    {class_name}Dto delete(UUID id);
  
}}
"""


def generate_service_interface_implementation(table_name, columns, package_prefix):
    class_name = make_class_name(table_name)
    var_name = class_name[0].lower() + class_name[1:]
    
    patch_statements = []
    
    for col_name, data_type in columns.items():
        java_type = sql_to_java_type(data_type)
        if col_name == 'id':
            continue
        patch_statements.append(f"""
      if (dto.get{snake_to_camel(col_name.capitalize())}() != null) {{
          entity.set{snake_to_camel(col_name.capitalize())}({ "UUID.fromString(" if java_type == "UUID" else "" }dto.get{snake_to_camel(col_name.capitalize())}(){ ")" if java_type == "UUID" else "" });
      }}""")
    
    return f"""\
package {package_prefix}.services.implementations;

import {package_prefix}.services.interfaces.{class_name}Service;
import {package_prefix}.entities.{class_name}Entity;
import {package_prefix}.dto.{class_name}Dto;
import {package_prefix}.repositories.{class_name}Repository;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.UUID;




@Service
public class {class_name}ServiceImpl implements {class_name}Service {{
 
    private final {class_name}Repository {var_name}Repository;
    
    public {class_name}ServiceImpl(
        {class_name}Repository {var_name}Repository
    ) {{
        this.{var_name}Repository = {var_name}Repository;
    }}
    
    
    @Override
    public {class_name}Dto getById(UUID id) {{
        {class_name}Entity entity = this.{var_name}Repository.findById(id).orElse(null);
        if (entity == null || entity.getDeletedAtUtc() != null) {{
            return null;
        }}
        return {class_name}Dto.fromEntity(entity);
    }}
    
    @Override
    public {class_name}Dto create({class_name}Dto dto) {{
      if (dto == null) {{
        throw new IllegalArgumentException("DTO cannot be null");
      }}
      {class_name}Entity entity = {class_name}Dto.toEntity(dto);
      return {class_name}Dto.fromEntity(this.{var_name}Repository.save(entity));
    }}
    
    @Override
    public {class_name}Dto update(UUID id, {class_name}Dto dto) {{
      if (dto == null) {{
        throw new IllegalArgumentException("DTO cannot be null");
      }}
      
      {class_name}Entity entity = this.{var_name}Repository.findById(id).orElse(null);
      if (entity == null || entity.getDeletedAtUtc() != null) {{
          throw new IllegalArgumentException("Entity with id " + id + " does not exist");
      }}
      if (!id.equals(entity.getId())) {{
        throw new IllegalArgumentException("Entity ID does not match path ID");
      }}
      
      {class_name}Entity savingEntity = {class_name}Dto.toEntity(dto);
      savingEntity.setId(entity.getId());
      savingEntity.setUpdatedAtUtc(LocalDateTime.now());
  
      return {class_name}Dto.fromEntity(this.{var_name}Repository.save(savingEntity));
    }}
    
    @Override
    public {class_name}Dto patch(UUID id, {class_name}Dto dto){{
      if (dto == null) {{
        throw new IllegalArgumentException("DTO cannot be null");
      }}
      
      {class_name}Entity entity = this.{var_name}Repository.findById(id).orElse(null);
      if (entity == null || entity.getDeletedAtUtc() != null) {{
          throw new IllegalArgumentException("Entity with id " + id + " does not exist");
      }}
      
      {"".join(patch_statements)}
      
      entity.setUpdatedAtUtc(LocalDateTime.now());
      
      return {class_name}Dto.fromEntity(this.{var_name}Repository.save(entity));
    }}
    
    @Override
    public {class_name}Dto delete(UUID id) {{
      if (id == null) {{
        throw new IllegalArgumentException("ID cannot be null");
      }}
      
      {class_name}Entity entity = this.{var_name}Repository.findById(id).orElse(null);
      if (entity == null || entity.getDeletedAtUtc() != null) {{
          throw new IllegalArgumentException("Entity with id " + id + " does not exist");
      }}
      
      entity.setDeletedAtUtc(LocalDateTime.now());
      return {class_name}Dto.fromEntity(this.{var_name}Repository.save(entity));
    }}
  
}}
"""




def generate_main_service_interface(service_name, package_prefix, import_configs, datasources_package_prefix):
    class_name = make_class_name(service_name, False)
    
    return f"""\
package {package_prefix}.services.interfaces;

import {datasources_package_prefix}.dto.*;
import java.util.UUID;


public interface {class_name}Service {{
  
  
  
}}
"""


def generate_main_service_interface_implementation(service_name, package_prefix, import_configs, datasources_package_prefix):
# {'\n'.join([ import_config['import_stmts'] for import_config in import_configs])}
    class_name = make_class_name(service_name, False)
    
    return f"""\
package {package_prefix}.services.implementations;

import org.springframework.data.jpa.domain.Specification;
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


def generate_typescript_types_classes(table_name, columns):
    class_name = make_class_name(table_name)
    
    fields = []
    
    for col_name, data_type in columns.items():
        ts_type = sql_to_typescript_type(data_type)
        
        fields.append(f"{snake_to_camel(col_name)}: {ts_type}")
    
    return f"""\
export type {class_name}Type = {{
{",\n".join([ f"  {f}" for f in fields])}
}}

export interface {class_name}Interface {{
{",\n".join([ f"  {f}" for f in fields])}
}}

export class {class_name}Entity implements {class_name}Interface {{

  constructor(
{",\n".join([ f"    public {f}" for f in fields])}
  ) {{}}

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
        if (entity == null) {{
            return null;
        }}
        return new {class_name}Dto(
{',\n'.join(getters)}
        );
    }}
    
    public static {class_name}Entity toEntity({class_name}Dto dto) {{
        if (dto == null) {{
            return null;
        }}
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

import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;
import {package_prefix}.entities.{class_name}Entity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.domain.Specification;
import java.util.UUID;


@Repository
public interface {class_name}Repository extends JpaRepository<{class_name}Entity, UUID>, JpaSpecificationExecutor<{class_name}> {{}}

"""

def generate_service_controller(table_name, service_name, app_package_prefix):
    class_name = make_class_name(table_name)
    url_name = '-'.join((table_name.split('.')[-1]).split('_'))
    

    return f"""\
package {app_package_prefix}.datasources.{service_name}.controllers;

import {app_package_prefix}.datasources.{service_name}.services.interfaces.{class_name}Service;
import {app_package_prefix}.datasources.{service_name}.dto.{class_name}Dto;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.util.UUID;
import {app_package_prefix}.domain.responses.DataResponse;


/* Disabled by default */
// @RestController
// @RequestMapping("/{url_name}")
public class {class_name}Controller {{

    private final {class_name}Service {service_name}Service;
    
    public {class_name}Controller(
      {class_name}Service {service_name}Service
    ) {{
        this.{service_name}Service = {service_name}Service;
    }}
    
    @GetMapping(value = "/{{id}}")
    public DataResponse<{class_name}Dto> getById(@PathVariable UUID id) {{
        return new DataResponse<>(this.{service_name}Service.getById(id));
    }}
    
    @PostMapping
    public DataResponse<{class_name}Dto> create(@RequestBody {class_name}Dto dto) {{
        return new DataResponse<>(this.{service_name}Service.create(dto));
    }}
    
    @PutMapping(value = "/{{id}}")
    public DataResponse<{class_name}Dto> update(@PathVariable UUID id, @RequestBody {class_name}Dto dto) {{
        return new DataResponse<>(this.{service_name}Service.update(id, dto));
    }}
    
    @PatchMapping(value = "/{{id}}")
    public DataResponse<{class_name}Dto> patch(@PathVariable UUID id, @RequestBody {class_name}Dto dto) {{
        return new DataResponse<>(this.{service_name}Service.patch(id, dto));
    }}
    
    @DeleteMapping(value = "/{{id}}")
    public DataResponse<{class_name}Dto> delete(@PathVariable UUID id) {{
        return new DataResponse<>(this.{service_name}Service.delete(id));
    }}
    

}}

"""

def generate_main_service_controller(service_name, package_prefix):
    class_name = make_class_name(service_name, False)

    return f"""\
package {package_prefix}.controllers;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;
import java.util.UUID;
import {package_prefix}.services.interfaces.{class_name}Service;
import {package_prefix}.domain.responses.DataResponse;
import {package_prefix}.domain.responses.JwtResults;
import {package_prefix}.datasources.{sql_config['service']}.dto.*;



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


def generate_datasource_config(service_name, package_prefix):
    class_name = make_class_name(service_name, False)
  
    # When specifying multiple datasources in a spring boot app, at least one needs the @Primary annotation
    # This is the one that will be used by default
    return f"""\
package {package_prefix}.config.datasources;

import org.springframework.context.annotation.Primary;
import jakarta.persistence.EntityManagerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.boot.orm.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import javax.sql.DataSource;
import java.util.Map;
import java.util.Objects;

@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(
    basePackages = "{package_prefix}.datasources.{service_name}",
    entityManagerFactoryRef = "EntityManager-{class_name}DB",
    transactionManagerRef = "EntityTransactionManager-{class_name}DB"
)
public class DatasourceJpaConfig{class_name}Db {{

    private final String packageScanPath{class_name}Db = "{package_prefix}.datasources.{service_name}";

    @Bean(name = "Datasource-{class_name}DB")
    public DataSource Datasource{class_name}Db(
        @Value("${{spring.datasource.microservice.{service_name}.url}}") String url,
        @Value("${{spring.datasource.microservice.{service_name}.username}}") String username,
        @Value("${{spring.datasource.microservice.{service_name}.password}}") String password,
        @Value("${{spring.datasource.microservice.{service_name}.driver-class-name}}") String driverClassName
    ) {{
        return DataSourceBuilder.create()
            .url(url)
            .username(username)
            .password(password)
            .driverClassName(driverClassName)
            .build();
    }}

    @Bean("EntityManager-{class_name}DB")
    public LocalContainerEntityManagerFactoryBean entityManagerFactory{class_name}Db(
        @Qualifier("Datasource-{class_name}DB") DataSource dataSource,
        @Value("${{spring.datasource.microservice.{service_name}.schema}}") String pgSchema,
        @Value("${{spring.datasource.microservice.{service_name}.hibernate.dialect}}") String hibernateDialect,
        EntityManagerFactoryBuilder builder
    ) {{
        return builder
            .dataSource(dataSource)
            .packages(this.packageScanPath{class_name}Db)
            .properties(Map.ofEntries(
                Map.entry("hibernate.default_schema", pgSchema),
                Map.entry("hibernate.dialect", hibernateDialect)
            ))
            .build();
    }}

    @Bean("EntityTransactionManager-{class_name}DB")
    public PlatformTransactionManager transactionManager{class_name}Db(
        @Qualifier("EntityManager-{class_name}DB") LocalContainerEntityManagerFactoryBean entityManager{class_name}Db
    ) {{
        EntityManagerFactory emf = Objects.requireNonNull(entityManager{class_name}Db.getObject());
        return new JpaTransactionManager(emf);
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
@Table(name = "{table_name.split('.')[-1] if '.' in table_name else table_name}")
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
    typescript_types_classes = {}
    repositories = {}
    service_interfaces = {}
    service_implementations = {}
    controllers = {}
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
        service_implementations[table_name] = generate_service_interface_implementation(table_name, columns, datasources_package_prefix)
        controllers[table_name] = generate_service_controller(table_name, service_name, app_package_prefix)
        typescript_types_classes[table_name] = generate_typescript_types_classes(table_name, columns)
        
        import_configs_by_table = generate_main_service_import_config(table_name, datasources_package_prefix)
        import_configs.append(import_configs_by_table)
        
    main_datasource_config = generate_datasource_config(service_name, app_package_prefix)
    main_service_interface = generate_main_service_interface(service_name, app_package_prefix, import_configs, datasources_package_prefix)
    main_service_implementation = generate_main_service_interface_implementation(service_name, app_package_prefix, import_configs, datasources_package_prefix)
    main_controller = generate_main_service_controller(service_name, app_package_prefix)

    return {
      'entities': entities,
      'dto': dto,
      'typescript_types_classes': typescript_types_classes,
      'repositories': repositories,
      'controllers': controllers,
      'service_interfaces': service_interfaces,
      'service_implementations': service_implementations,
      'main_datasource_config': main_datasource_config,
      'main_service_interface': main_service_interface,
      'main_service_implementation': main_service_implementation,
      'main_controller': main_controller,
    }


def write_to_file(contents, path_full):
    output_dir = os.path.dirname(path_full)
    
    os.makedirs(output_dir, exist_ok=True)
    with open(path_full, 'w') as file:
      file.write(contents)
                    
def write_items_to_files(items: list, output_dir: str, classNameSuffix: str = None, makeFileName: lambda n: str = None):
     for table_name, code in items.items():
        class_name = make_class_name(table_name)
        file_path = os.path.join(output_dir, makeFileName(table_name) if makeFileName else f"{class_name}{classNameSuffix}.java")
        write_to_file(code, file_path)
            
    #  os.makedirs(output_dir, exist_ok=True)
    #  for table_name, code in items.items():
    #     class_name = make_class_name(table_name)
    #     file_path = os.path.join(output_dir, f"{class_name}{classNameSuffix}.java")
    #     with open(file_path, 'w') as file:
    #         file.write(code)
          



if __name__ == "__main__":
    """
    SQL file table definitions are expected to be in the following format:
    
    CREATE TABLE IF NOT EXISTS {table_name} (
        {column_name} {data_type in UPPERCASE} NOT NULL etc...,
    );
    
    Example:
    
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        metadata JSONB DEFAULT NULL,
        created_at_utc TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at_utc TIMESTAMP DEFAULT NULL,
        deleted_at_utc TIMESTAMP DEFAULT NULL
    );
    """
    
    sql_configs = [
      # format: { "service": "service_name", "sql_path": "full/path/to/sql_file.sql" }
      
    ]
    
    if os.path.exists("src"):
      shutil.rmtree("src")
      
    for sql_config in sql_configs:
      # print("processing: ", sql_configs)
      
      results = parse_sql_file(sql_config)
      
      write_items_to_files(items = results['entities'], classNameSuffix = "Entity", output_dir = f'src/datasources/{sql_config['service']}/entities')
      write_items_to_files(items = results['dto'], classNameSuffix = "Dto", output_dir = f'src/datasources/{sql_config['service']}/dto')
      write_items_to_files(items = results['typescript_types_classes'], makeFileName = lambda n: f"{singularize_word(n)}.types.ts", output_dir = f'src/datasources/{sql_config['service']}/typescript')
      write_items_to_files(items = results['repositories'], classNameSuffix = "Repository", output_dir = f'src/datasources/{sql_config['service']}/repositories')
      write_items_to_files(items = results['controllers'], classNameSuffix = "Controller", output_dir = f'src/datasources/{sql_config['service']}/controllers')
      write_items_to_files(items = results['service_interfaces'], classNameSuffix = "Service", output_dir = f'src/datasources/{sql_config['service']}/services/interfaces')
      write_items_to_files(items = results['service_implementations'], classNameSuffix = "ServiceImpl", output_dir = f'src/datasources/{sql_config['service']}/services/implementations')
      
      write_to_file(contents = results['main_datasource_config'], path_full = f'src/configs/DatasourceJpaConfig{make_class_name(sql_config['service'], False)}Db.java')
      write_to_file(contents = results['main_service_interface'], path_full = f'src/services/interfaces/{make_class_name(sql_config['service'], False)}Service.java')
      write_to_file(contents = results['main_service_implementation'], path_full = f'src/services/implementations/{make_class_name(sql_config['service'], False)}ServiceImpl.java')
      write_to_file(contents = results['main_controller'], path_full = f'src/controllers/{make_class_name(sql_config['service'], False)}Controller.java')
    # END for
      
    print("Resource classes generated successfully")
