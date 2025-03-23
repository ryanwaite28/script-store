# a few custom logic here and there, but mostly general purpose code
# to generate spring jpa entities from sql files
# the code is not perfect, but it's a good starting point

import re, os, shutil, codecs



error_code_counter = 0



def rot13_codec(text):
  """Encrypts or decrypts text using ROT13 via the codecs module."""
  return codecs.encode(text, 'rot13')

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


def snake_to_camel(snake_string):
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
  
def make_class_name(table_name, singularize = True):
  table_name_split = (table_name.split('.')[-1]).split('_')
  # print("[make_class_name] before", table_name_split)
  if singularize:
    table_name_split[-1] = singularize_word(table_name_split[-1])
  # print("[make_class_name] after", table_name_split)
  class_name = ''.join(word.capitalize() for word in table_name_split)
  return snake_to_camel(class_name)


def java_cast_to_type(sql_type, value):
    if 'UUID' in sql_type:
        return f"UUID.fromString({value})"
    if 'INT' in sql_type:
        return f'Integer.valueOf({value})'
    if 'BIGINT' in sql_type:
        return f'BigInteger.valueOf({value})'
    if 'BOOLEAN' in sql_type:
        return f'Boolean.valueOf({value})'
    elif ('VARCHAR' in sql_type or 'TEXT' in sql_type or 'JSON' in sql_type or 'JSOB' in sql_type):
        return f'String.valueOf({value})'
    elif 'DATE' in sql_type or 'TIMESTAMP' in sql_type:
        return f'LocalDateTime.parse({value})'
    elif 'DOUBLE' in sql_type or 'DECIMAL' in sql_type:
        return f'Double.valueOf({value})'
    else:
        return value

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


def generate_service_interface(table_name, app_package_prefix, package_prefix):
    class_name = make_class_name(table_name)
    
    return f"""\
package {package_prefix}.services.interfaces;

import {app_package_prefix}.domain.responses.PaginationResponse;
import {package_prefix}.dto.{class_name}Dto;
import {package_prefix}.dto.searches.{class_name}SearchParams;
import java.util.UUID;
import java.util.Map;

public interface {class_name}Service {{
  
    PaginationResponse<{class_name}Dto> search{class_name}(Map<String, String> queryParams);
    
    PaginationResponse<{class_name}Dto> search{class_name}({class_name}SearchParams params);
    
    {class_name}Dto getById(UUID id);
    
    {class_name}Dto create(UUID userId, {class_name}Dto dto);
    
    {class_name}Dto update(UUID userId, UUID id, {class_name}Dto dto);
    
    {class_name}Dto patch(UUID userId, UUID id, {class_name}Dto dto);
    
    {class_name}Dto delete(UUID userId, UUID id);
  
}}
"""


def generate_service_interface_implementation(table_name, columns, app_package_prefix, package_prefix):
    class_name = make_class_name(table_name)
    var_name = class_name[0].lower() + class_name[1:]
    
    
    patch_statements = []
    update_statements = []
    
    search_predicates = []
    
    
    # cb.equal(root.get(\"{snake_to_camel(col_name)}\"), params.{snake_to_camel(col_name)}())
    
    # lambda to pick cb.equal, cb.like, etc based on data type
    # def get_predicate_method(data_type):
    
    for col_name, data_type in columns.items():
        java_type = sql_to_java_type(data_type)
        if col_name == 'id':
            continue
        patch_statements.append(f"""
        if (dto.get{snake_to_camel(col_name.capitalize())}() != null) {{
            entity.set{snake_to_camel(col_name.capitalize())}({ "UUID.fromString(" if java_type == "UUID" else "" }dto.get{snake_to_camel(col_name.capitalize())}(){ ")" if java_type == "UUID" else "" });
        }}""")
        
        update_statements.append(f"""entity.set{snake_to_camel(col_name.capitalize())}({ f"dto.get{snake_to_camel(col_name.capitalize())}() == null ? null : " if java_type == "UUID" else "" }{ "UUID.fromString(" if java_type == "UUID" else "" }dto.get{snake_to_camel(col_name.capitalize())}(){ ")" if java_type == "UUID" else "" });""")
        
        search_predicates.append(f"if (params.{snake_to_camel(col_name)}() != null) {{\n                predicates.add(cb.equal(root.get(\"{snake_to_camel(col_name)}\"), params.{snake_to_camel(col_name)}()));\n            }}")
        
        
    
    return f"""\
package {package_prefix}.services.implementations;

import {package_prefix}.exceptions.DomainException;
import {package_prefix}.exceptions.DomainRuntimeException;
import {app_package_prefix}.utils.RequestParamsUtils;
import {app_package_prefix}.domain.responses.PaginationResponse;
import {package_prefix}.dto.searches.{class_name}SearchParams;
import {package_prefix}.enums.errorcodes.{class_name}ErrorCodes;
import {package_prefix}.enums.modelevents.{class_name}ModelEvents;
import {package_prefix}.services.interfaces.{class_name}Service;
import {package_prefix}.entities.{class_name}Entity;
import {package_prefix}.dto.{class_name}Dto;
import {package_prefix}.repositories.{class_name}Repository;
import org.springframework.stereotype.Service;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpStatus;
import java.time.LocalDateTime;
import java.util.UUID;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;



@Service
public class {class_name}ServiceImpl implements {class_name}Service {{
 
    private final {class_name}Repository {var_name}Repository;
    
    public {class_name}ServiceImpl({class_name}Repository {var_name}Repository) {{
        this.{var_name}Repository = {var_name}Repository;
    }}
    
    
    
    @Override
    public PaginationResponse<{class_name}Dto> search{class_name}(Map<String, String> queryParams) {{
        if (queryParams == null) {{
            throw new IllegalArgumentException("Search params cannot be null");
        }}

        int queryOffset = queryParams.containsKey("offset") ? Integer.parseInt(queryParams.get("offset")) : 0;
        int queryLimit = queryParams.containsKey("limit") ? Integer.parseInt(queryParams.get("limit")) : 10;

        Specification<{class_name}Entity> querySpec = RequestParamsUtils.convertParamsToSearchPredicates(queryParams, {class_name}Entity.class);

        Pageable pageable = PageRequest.of(queryOffset, queryLimit);

        Page<{class_name}Entity> pageResults = this.{var_name}Repository.findAll(querySpec, pageable);

        List<{class_name}Dto> resultsData = pageResults.getContent().stream().map({class_name}Dto::fromEntity).toList();
        Integer offset = pageResults.getNumber();
        Integer limit = pageResults.getSize();
        Integer page = pageResults.getNumber() + 1;
        Integer pages = pageResults.getTotalPages();
        Integer resultsCount = resultsData.size();
        Long tableCount = this.{var_name}Repository.count();

        return new PaginationResponse<>(
            resultsData,
            resultsCount,
            tableCount,
            offset,
            limit,
            page,
            pages
        );
    }}
    
    @Override
    public PaginationResponse<{class_name}Dto> search{class_name}({class_name}SearchParams params) {{
        if (params == null) {{
            throw new IllegalArgumentException("Search params cannot be null");
        }}
        
        Pageable pageable = PageRequest.of(params.offset(), params.limit());
        Specification<{class_name}Entity> spec = (root, query, cb) -> {{
            List<Predicate> predicates = new ArrayList<>();
            
{"\n".join([ f"            {s}" for s in search_predicates])}
            
            return cb.and(predicates.toArray(new Predicate[0]));
        }};
        
        Page<{class_name}Entity> pageResults = this.{var_name}Repository.findAll(spec, pageable);
        
        List<{class_name}Dto> resultsData = pageResults.getContent().stream().map({class_name}Dto::fromEntity).toList();
        Integer offset = pageResults.getNumber();
        Integer limit = pageResults.getSize();
        Integer page = pageResults.getNumber() + 1;
        Integer pages = pageResults.getTotalPages();
        Integer resultsCount = resultsData.size();
        Long tableCount = this.{var_name}Repository.count();
        
        return new PaginationResponse<>(
            resultsData,
            resultsCount,
            tableCount,
            offset,
            limit,
            page,
            pages
        );
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
    public {class_name}Dto create(UUID userId, {class_name}Dto dto) {{
        this.validateCreate{class_name}Dto(userId, dto);
        
        // using builder to control which fields are set for creation
        {class_name}Entity entity = {class_name}Dto.toEntity(
            {class_name}Dto.builder()
{'\n'.join([f"                .{snake_to_camel(col_name)}(dto.get{snake_to_camel(col_name.capitalize())}())" for col_name, data_type in columns.items()])}
                .build()
        );
        
        return {class_name}Dto.fromEntity(this.{var_name}Repository.save(entity));
    }}
    
    @Override
    public {class_name}Dto update(UUID userId, UUID id, {class_name}Dto dto) {{
        this.validateUpdate{class_name}Dto(userId, id, dto);
        
        {class_name}Entity entity = this.{var_name}Repository.findById(id).orElse(null);
        if (entity == null || entity.getDeletedAtUtc() != null) {{
            throw new IllegalArgumentException("Entity with id " + id + " does not exist");
        }}

        // manually setting entity fields for update to control which fields are updated
{"\n".join([ f"        {s}" for s in update_statements])}

        entity.setUpdatedAtUtc(LocalDateTime.now());
    
        return {class_name}Dto.fromEntity(this.{var_name}Repository.save(entity));
    }}
    
    @Override
    public {class_name}Dto patch(UUID userId, UUID id, {class_name}Dto dto){{
        this.validatePatch{class_name}Dto(userId, id, dto);
        
        {class_name}Entity entity = this.{var_name}Repository.findById(id).orElse(null);
        if (entity == null || entity.getDeletedAtUtc() != null) {{
            throw new IllegalArgumentException("Entity with id " + id + " does not exist");
        }}
        
        {"".join(patch_statements)}
        
        entity.setUpdatedAtUtc(LocalDateTime.now());
        
        return {class_name}Dto.fromEntity(this.{var_name}Repository.save(entity));
    }}
    
    @Override
    public {class_name}Dto delete(UUID userId, UUID id) {{
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
    
    
    private void validateRequirements({class_name}Dto dto) {{
        // this is validations common on both create and update
    }}
    
    private void validateCreate{class_name}Dto(UUID userId, {class_name}Dto dto) {{
        this.validateRequirements(dto);
        if (dto == null) {{
            throw new DomainRuntimeException("DTO was null", HttpStatus.BAD_REQUEST, {class_name}ErrorCodes.InvalidData);
        }}
        
        if (dto.getId() != null) {{
            throw new IllegalArgumentException("ID must be null");
        }}
    }}
    
    private void validateUpdate{class_name}Dto(UUID userId, UUID id, {class_name}Dto dto) {{
        this.validateRequirements(dto);
        if (dto == null) {{
            throw new DomainRuntimeException("DTO was null", HttpStatus.BAD_REQUEST, {class_name}ErrorCodes.InvalidData);
        }}
        
        if (dto.getId() == null) {{
            throw new IllegalArgumentException("ID must be null");
        }}
    }}
    
    private void validatePatch{class_name}Dto(UUID userId, UUID id, {class_name}Dto dto) {{
        this.validateRequirements(dto);
        if (dto == null) {{
            throw new DomainRuntimeException("DTO was null", HttpStatus.BAD_REQUEST, {class_name}ErrorCodes.InvalidData);
        }}
        
        if (dto.getId() == null) {{
            throw new IllegalArgumentException("ID must be null");
        }}
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

import org.springframework.stereotype.Service;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
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
    var_name = class_name[0].lower() + class_name[1:]
    
    typed_fields = []
    fields = []
    
    for col_name, data_type in columns.items():
        ts_type = sql_to_typescript_type(data_type)
        
        typed_fields.append(f"{snake_to_camel(col_name)}: {ts_type}")
        fields.append(f"{snake_to_camel(col_name)}")
        
    
    return f"""\
export type {class_name}Type = {{
{",\n".join([ f"  {f}" for f in typed_fields])}
}}

export interface {class_name}Interface {{
{",\n".join([ f"  {f}" for f in typed_fields])}
}}

export class {class_name}Entity implements {class_name}Interface {{

  constructor(
{",\n".join([ f"    public {f}" for f in typed_fields])}
  ) {{}}
  
  public static fromDto({var_name}: {class_name}Type): {class_name}Entity {{
    return new {class_name}Entity(
{",\n".join([ f"      {var_name}.{f}" for f in fields])}
    );
  }}
  
  public toDto(): {class_name}Type {{
    return {{
{",\n".join([ f"      {f}: this.{f}" for f in fields])}
    }};
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

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
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
@JsonIgnoreProperties(ignoreUnknown = true)
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


# def generate_fields_types_map(table_name, columns, package_prefix):
#     class_name = make_class_name(table_name)
    
#     fields = []
#     getters = []
    
#     for col_name, data_type in columns.items():
#         java_type = sql_to_java_type(data_type)
#         fields.append(f"    private {"String" if (java_type == 'UUID') else f"String" if ("JSON" in data_type) else java_type} {snake_to_camel(col_name)};")
#         getters.append(f"            entity.get{snake_to_camel(col_name.capitalize())}(){".toString()" if (java_type == 'UUID') else ""}")
    
#     return f"""\
# package {package_prefix}.dto;

# import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
# import com.fasterxml.jackson.annotation.JsonInclude;
# import {package_prefix}.entities.{class_name}Entity;
# import lombok.Data;
# import lombok.Builder;
# import lombok.AllArgsConstructor;
# import lombok.NoArgsConstructor;
# import java.time.LocalDateTime;
# import java.util.UUID;

# @Data
# @Builder
# @AllArgsConstructor
# @NoArgsConstructor
# @JsonIgnoreProperties(ignoreUnknown = true)
# public class {class_name}FieldsType {{

# {"\n".join(fields)}

#     public static {class_name}Dto fromEntity({class_name}Entity entity) {{
#         if (entity == null) {{
#             return null;
#         }}
#         return new {class_name}Dto(
# {',\n'.join(getters)}
#         );
#     }}
    
#     public static {class_name}Entity toEntity({class_name}Dto dto) {{
#         if (dto == null) {{
#             return null;
#         }}
#         return {class_name}Entity.builder()
# {'\n'.join([f"            .{snake_to_camel(col_name)}({ "UUID.fromString(" if sql_to_java_type(data_type) == "UUID" else "" }dto.get{snake_to_camel(col_name.capitalize())}(){ ")" if sql_to_java_type(data_type) == "UUID" else "" })" for col_name, data_type in columns.items()])}
#             .build();
#     }}

# }}
# """


def generate_search_params_class(table_name, columns, package_prefix):
    class_name = make_class_name(table_name)
    
    fields = []
    constructor_args = []
    
    # queryParams.getOrDefault(\"{snake_to_camel(col_name)}\", null)
    
    for col_name, data_type in columns.items():
        java_type = sql_to_java_type(data_type)
        fields.append(f"    {java_type} {snake_to_camel(col_name)}")
        # build constructor args from query params map
        constructor_args.append(f"      {f"!queryParams.containsKey(\"{snake_to_camel(col_name)}\") || queryParams.get(\"{snake_to_camel(col_name)}\") == null"} ? null : {java_cast_to_type(data_type, f"queryParams.get(\"{snake_to_camel(col_name)}\")")}")
    
    return f"""\
package {package_prefix}.dto.searches;

import java.time.LocalDateTime;
import java.util.UUID;
import java.util.Map;

public record {class_name}SearchParams(
{",\n".join([ f"{f}" for f in fields])},
    Integer offset,
    Integer limit
) {{
  
    public {class_name}SearchParams(Map<String, String> queryParams) {{
        this(
{',\n'.join([ f"      {f}" for f in constructor_args])},
            Integer.parseInt(queryParams.getOrDefault("offset", "0")),
            Integer.parseInt(queryParams.getOrDefault("limit", "10"))
        );
    }}
  
}}
"""


def generate_model_names_enum(service_name, table_names, app_package_prefix):
    use_service_name = make_class_name(service_name, False)
    enum_values = []
    
    for table_name in table_names:
        enum_values.append(f"    {singularize_word(table_name.split('.')[1]).upper()}")
    
    return f"""\
package {app_package_prefix}.enums;

public enum {use_service_name}ModelNames {{
{",\n".join(enum_values)},
    ;
    
    public static {use_service_name}ModelNames fromString(String name) {{
        for ({use_service_name}ModelNames model : {use_service_name}ModelNames.values()) {{
            if (model.name().equalsIgnoreCase(name)) {{
                return model;
            }}
        }}
        return null;
    }}
}}
"""


def generate_model_events_enum(table_name, columns, package_prefix):
    class_name = make_class_name(table_name)
    enum_value_name = singularize_word(table_name.split('.')[-1]).upper()
    
    enum_values_per_field = []
    
    for col_name, data_type in columns.items():
        java_type = sql_to_java_type(data_type)
        enum_values_per_field.append(f"    {enum_value_name}_{col_name.upper()}_CREATED")
        enum_values_per_field.append(f"    {enum_value_name}_{col_name.upper()}_UPDATED")
        enum_values_per_field.append(f"    {enum_value_name}_{col_name.upper()}_DELETED")
    
    return f"""\
package {package_prefix}.enums.modelevents;

public enum {class_name}ModelEvents {{
    {enum_value_name}_CREATED,
    {enum_value_name}_UPDATED,
    {enum_value_name}_DELETED,
    
{",\n".join(enum_values_per_field)},
    ;
}}
"""




def generate_exception(table_name, package_prefix, app_package_prefix, exception_type):
    class_name = make_class_name(table_name)
    
    return f"""\
package {package_prefix}.exceptions;

import {app_package_prefix}.exceptions.DomainException;
import {app_package_prefix}.exceptions.DomainRuntimeException;

public class {class_name}{exception_type} extends DomainRuntimeException {{
    
    public {class_name}{exception_type}(String message) {{
        super(message);
    }}
    
    public {class_name}{exception_type}(String message, Throwable cause) {{
        super(message, cause);
    }}
    
    public {class_name}{exception_type}(Throwable cause) {{
        super(cause);
    }}

}}
"""


def generate_error_codes(table_name, app_package_prefix, package_prefix):
    class_name = make_class_name(table_name)
    
    def increment_error_code():
        global error_code_counter
        error_code_counter += 1
        return error_code_counter
    
    return f"""\
package {package_prefix}.enums.errorcodes;

import {app_package_prefix}.interfaces.ErrorCode;
import lombok.Getter;

public enum {class_name}ErrorCodes implements ErrorCode {{
    
    NotFound({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} not found"),
    CreateFailed({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data could not be created"),
    SearchFailed({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data search failed"),
    UpdateFailed({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data could not be updated"),
    PatchFailed({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data could not be patched"),
    DeleteFailed({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data could not be deleted"),
    Locked({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data is locked"),
    Corrupted({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data is corrupted"),
    InvalidData({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data is invalid"),
    InvalidState({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data is in an invalid state"),
    InvalidOperation({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data operation is invalid"),
    InvalidRequest({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} request is invalid"),
    ProcessingFailed({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} data processing failed"),
    UnexpectedError({increment_error_code()}, "{rot13_codec(class_name)}", "{class_name} - unexpected error occurred"),
    ;
    
    @Getter
    private int errorId;

    @Getter
    private String errorClass;
    
    @Getter
    private String errorMessage;

    {class_name}ErrorCodes(int errorId, String errorClass, String errorMessage) {{
        this.errorId = errorId;
        this.errorClass = errorClass;
        this.errorMessage = errorMessage;
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
public interface {class_name}Repository extends JpaRepository<{class_name}Entity, UUID>, JpaSpecificationExecutor<{class_name}Entity> {{}}

"""

def generate_service_controller(table_name, service_name, columns, app_package_prefix):
    class_name = make_class_name(table_name)
    url_name = '-'.join((table_name.split('.')[-1]).split('_'))
    var_name = class_name[0].lower() + class_name[1:]
    
    request_params = []
    service_arguments = []
    
    for col_name, data_type in columns.items():
        java_type = sql_to_java_type(data_type)
        field_var_name = snake_to_camel(col_name)
        request_params.append(f"@RequestParam(value = \"{field_var_name}\", required = false) {"String" if (java_type == 'UUID') else f"String" if ("JSON" in data_type) else java_type} {field_var_name}")
        service_arguments.append(f"{field_var_name}")
    

### old way
# @GetMapping("/search")
#     public PaginationResponse<{class_name}Dto> searchInterviewAuthorities(
# {",\n".join([ f"        {f}" for f in request_params])},

#         @RequestParam(value = "offset", required = false) Integer offset,
#         @RequestParam(value = "limit", required = false) Integer limit
#     ) {{
#         return this.{var_name}Service.search{class_name}(new {class_name}SearchParams(
# {",\n".join([ f"            {f}" for f in service_arguments])},
            
#             offset != null ? offset : 0,
#             limit != null ? limit : 10
#         ));
#     }}


    return f"""\
package {app_package_prefix}.datasources.{service_name}.controllers;

import {app_package_prefix}.configs.jwt.JwtAuthorized;
import {app_package_prefix}.datasources.{service_name}.services.interfaces.{class_name}Service;
import {app_package_prefix}.datasources.{service_name}.dto.{class_name}Dto;
import {app_package_prefix}.datasources.{service_name}.dto.searches.{class_name}SearchParams;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import {app_package_prefix}.domain.responses.PaginationResponse;
import java.io.IOException;
import java.util.UUID;
import java.util.Map;
import java.time.LocalDateTime;
import {app_package_prefix}.domain.responses.DataResponse;


/* Disabled by default */
// @RestController
// @RequestMapping("/{url_name}")
public class {class_name}Controller {{

    private final {class_name}Service {var_name}Service;
    
    public {class_name}Controller(
      {class_name}Service {var_name}Service
    ) {{
        this.{var_name}Service = {var_name}Service;
    }}
    
    
    
    @GetMapping("/search")
    public PaginationResponse<{class_name}Dto> search{class_name}(@RequestParam() Map<String, String> queryParams) {{
        return this.{var_name}Service.search{class_name}(queryParams);
    }}
    
    @GetMapping(value = "/{{id}}")
    public DataResponse<{class_name}Dto> getById(@PathVariable UUID id) {{
        return new DataResponse<>(this.{var_name}Service.getById(id));
    }}
    
    @JwtAuthorized
    @PostMapping
    public DataResponse<{class_name}Dto> create(
      @RequestAttribute("AUTH_USER_ID") UUID userId,
      @RequestBody {class_name}Dto dto
    ) {{
        return new DataResponse<>(this.{var_name}Service.create(userId, dto));
    }}
    
    @JwtAuthorized
    @PutMapping(value = "/{{id}}")
    public DataResponse<{class_name}Dto> update(
      @RequestAttribute("AUTH_USER_ID") UUID userId,
      @PathVariable UUID id, 
      @RequestBody {class_name}Dto dto
    ) {{
        return new DataResponse<>(this.{var_name}Service.update(userId, id, dto));
    }}
    
    @JwtAuthorized
    @PatchMapping(value = "/{{id}}")
    public DataResponse<{class_name}Dto> patch(
      @RequestAttribute("AUTH_USER_ID") UUID userId,
      @PathVariable UUID id, 
      @RequestBody {class_name}Dto dto
    ) {{
        return new DataResponse<>(this.{var_name}Service.patch(userId, id, dto));
    }}
    
    @JwtAuthorized
    @DeleteMapping(value = "/{{id}}")
    public DataResponse<{class_name}Dto> delete(
      @RequestAttribute("AUTH_USER_ID") UUID userId,
      @PathVariable UUID id
    ) {{
        return new DataResponse<>(this.{var_name}Service.delete(userId, id));
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


def generate_main_service_controller_advice(service_name, package_prefix):
    class_name = make_class_name(service_name, False)

    return f"""\
package {package_prefix}.controllers.advices;

import org.springframework.web.bind.annotation.*;
import java.io.IOException;
import org.springframework.http.HttpStatus;
import java.util.UUID;
import {package_prefix}.domain.responses.ErrorCodeResponse;
import {package_prefix}.exceptions.DomainException;
import {package_prefix}.exceptions.DomainRuntimeException;




@RestController
@RequestMapping("/{service_name}")
public class AppControllerAdvice {{

    @ExceptionHandler(DomainException.class)
    public ResponseEntity<ErrorCodeResponse> handle(DomainException ex) {{
        return new ResponseEntity<>(new ErrorCodeResponse(ex.getErrorCode()), ex.getHttpStatus());
    }}

    @ExceptionHandler(DomainRuntimeException.class)
    public ResponseEntity<ErrorCodeResponse> handle(DomainRuntimeException ex) {{
        return new ResponseEntity<>(new ErrorCodeResponse(ex.getErrorCode()), ex.getHttpStatus());
    }}

}}
"""



def generate_datasource_config(service_name, package_prefix):
    class_name = make_class_name(service_name, False)
  
    # When specifying multiple datasources in a spring boot app, at least one needs the @Primary annotation
    # This is the one that will be used by default
    return f"""\
package {package_prefix}.configs;

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
@ConditionalOnProperty(name = "", havingValue = "true", matchIfMissing = true)
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
    


def generate_main_services_enum(service_names, app_package_prefix):
    enum_values = []
    
    for service_name in service_names:
        enum_value_name = snake_to_camel(service_name).upper()
        enum_values.append(f"    {enum_value_name}_SERVICE")
    
    return f"""\
package {app_package_prefix}.enums;

public enum ServiceNames {{
  
{",\n".join(enum_values)},
    ;
    
    public static ServiceNames fromString(String name) {{
        for (ServiceNames service : ServiceNames.values()) {{
            if (service.name().equalsIgnoreCase(name)) {{
                return service;
            }}
        }}
        return null;
    }}
    
}}
"""
    
  
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

def parse_sql_file(sql_config, app_package_prefix):
    service_name = sql_config['service']
    sql_file_path = sql_config['sql_path']
    datasources_package_prefix = f"{app_package_prefix}.datasources.{sql_config['service']}"
  
  
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
    search_params = {}
    model_event_enums = {}
    import_configs: list = []
    
    not_found_exceptions = {}
    invalid_data_exceptions = {}
    processing_exceptions = {}
    
    error_codes = {}
    
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
        service_interfaces[table_name] = generate_service_interface(table_name, app_package_prefix, datasources_package_prefix)
        service_implementations[table_name] = generate_service_interface_implementation(table_name, columns, app_package_prefix, datasources_package_prefix)
        controllers[table_name] = generate_service_controller(table_name, service_name, columns, app_package_prefix)
        typescript_types_classes[table_name] = generate_typescript_types_classes(table_name, columns)
        search_params[table_name] = generate_search_params_class(table_name, columns, datasources_package_prefix)
        model_event_enums[table_name] = generate_model_events_enum(table_name, columns, datasources_package_prefix)
        
        import_configs_by_table = generate_main_service_import_config(table_name, datasources_package_prefix)
        import_configs.append(import_configs_by_table)
        
        not_found_exceptions[table_name] = generate_exception(table_name, datasources_package_prefix, app_package_prefix, 'NotFoundException')
        invalid_data_exceptions[table_name] = generate_exception(table_name, datasources_package_prefix, app_package_prefix, 'InvalidDataException')
        processing_exceptions[table_name] = generate_exception(table_name, datasources_package_prefix, app_package_prefix, 'ProcessingException')
        error_codes[table_name] = generate_error_codes(table_name, app_package_prefix, datasources_package_prefix)
        
    main_datasource_config = generate_datasource_config(service_name, app_package_prefix)
    main_service_interface = generate_main_service_interface(service_name, app_package_prefix, import_configs, datasources_package_prefix)
    main_service_implementation = generate_main_service_interface_implementation(service_name, app_package_prefix, import_configs, datasources_package_prefix)
    main_controller = generate_main_service_controller(service_name, app_package_prefix)
    main_controller_advice = generate_main_service_controller_advice(service_name, app_package_prefix)
    model_names_enum = generate_model_names_enum(service_name, [ table_name for table_name, columns_def in table_definitions ], app_package_prefix)
    
    # model_names_enum 

    return {
      'entities': entities,
      'dto': dto,
      'search_params': search_params,
      'model_event_enums': model_event_enums,
      'typescript_types_classes': typescript_types_classes,
      'repositories': repositories,
      'controllers': controllers,
      'service_interfaces': service_interfaces,
      'service_implementations': service_implementations,
      'main_datasource_config': main_datasource_config,
      'main_service_interface': main_service_interface,
      'main_service_implementation': main_service_implementation,
      'main_controller': main_controller,
      'main_controller_advice': main_controller_advice,
      'model_names_enum': model_names_enum,
      'not_found_exceptions': not_found_exceptions,
      'invalid_data_exceptions': invalid_data_exceptions,
      'processing_exceptions': processing_exceptions,
      'error_codes': error_codes,
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
          




def create_helper_classes(package_prefix):
    pagination_response_class = f"""\
package {package_prefix}.domain.responses;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.List;

public record PaginationResponse<T> (
    List<T> data,
    Integer resultsCount,
    Long tableCount,
    Integer offset,
    Integer limit,
    Integer page,
    Integer pages
) {{ }}
"""
    write_to_file(contents = pagination_response_class, path_full = f'src/domain/responses/PaginationResponse.java')
    
    
    data_response_class = f"""\
package {package_prefix}.domain.responses;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.List;

public record DataResponse<T>(T data) {{ }}
"""
    write_to_file(contents = data_response_class, path_full = f'src/domain/responses/DataResponse.java')
    
    
    results_response_class = f"""\
package {package_prefix}.domain.responses;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.List;

public record ResultsResponse<T>(
    T data,
    boolean error,
    String message
) {{ }}
"""
    write_to_file(contents = results_response_class, path_full = f'src/domain/responses/ResultsResponse.java')
    
    
    error_code_response_class = f"""\
package {package_prefix}.domain.responses;

import {package_prefix}.interfaces.ErrorCode;

public record ErrorCodeResponse(ErrorCode errorCode) {{ }}
"""
    write_to_file(contents = error_code_response_class, path_full = f'src/domain/responses/ErrorCodeResponse.java')
    
    
    coerce_utils = f"""\
package {package_prefix}.utils;


import java.util.function.Consumer;
import java.util.function.Function;

public class CoerceUtils {{

    public static <T,R> R returnOnNotNull(T obj, Function<T, R> fn) {{
        return obj == null ? null : fn.apply(obj);
    }}
    
    public static <T,R> void runOnNotNull(T obj, Consumer<T> fn) {{
        if (obj != null) {{
            fn.accept(obj);
        }}
    }}

    public static <T> T coalesceFalsy(T obj, T defaultValue) {{
        return obj != null ? obj : defaultValue;
    }}

}}
"""
    write_to_file(contents = coerce_utils, path_full = f'src/utils/CoerceUtils.java')
    
    
    common_utils = f"""\
package {package_prefix}.utils;

import org.springframework.web.multipart.MultipartFile;
import lombok.NonNull;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jdk8.Jdk8Module;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import jakarta.validation.constraints.NotNull;
import java.lang.reflect.Field;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.*;
import java.util.function.Predicate;
import java.util.regex.Matcher;

public class CommonUtils {{

    private final ObjectMapper objectMapper = new ObjectMapper()
        .registerModule(new Jdk8Module())
        .registerModule(new JavaTimeModule())
        ;

    public static <T extends Enum<T>> T enumFromName(Class<T> enumClass, String enumName) {{
        if (enumName == null) {{
            return null;
        }}
        for (T enumValue : enumClass.getEnumConstants()) {{
            if (enumName.equals(enumValue.name())) {{
                return enumValue;
            }}
        }}
        return null;
    }}

    public static <T extends Enum<T>> T enumByPredicate(Class<T> enumClass, @NonNull Predicate<T> predicate) {{
        for (T enumValue : enumClass.getEnumConstants()) {{
            if (predicate.test(enumValue)) {{
                return enumValue;
            }}
        }}
        return null;
    }}

    public static String makeUniqueFileNameFromFile(MultipartFile file) {{
        String[] fileNameSplit = file.getOriginalFilename().split("\\.");
        String extension = fileNameSplit[fileNameSplit.length - 1];
        return String.format("%s.%s.%s", UUID.randomUUID(), Instant.now().toEpochMilli(), extension);
    }}

    public static Map<String, Object> parseJsonString(String json) {{
        try {{
            ObjectMapper objectMapper = new ObjectMapper()
                .registerModule(new Jdk8Module())
                .registerModule(new JavaTimeModule())
                ;

            Map<String, Object> metadata = objectMapper.readValue(json, new TypeReference<Map<String, Object>>() {{}});
            return metadata;
        }}
        catch (JsonProcessingException e) {{
            throw new RuntimeException(e);
        }}
    }}

    public static Map<String, Class<?>> getClassFieldNamesAndTypes(Class<?> classDef) {{
        Field[] classFields = classDef.getDeclaredFields();
        Map<String, Class<?>> fieldDefs = new HashMap<>();

        for (Field field : classFields) {{
            fieldDefs.put(field.getName(), field.getType());
        }}

        return fieldDefs;
    }}

    public static List<String> getAllCapturesFromMatcher(Matcher matcher) {{
        List<String> captures = new ArrayList<>();
        // capture all top-level and query lists
        while (matcher.find()) {{
            String match = matcher.group();
            if (match == null) {{
                continue;
            }}
            if (!captures.contains(match)) {{
                captures.add(match);
            }}
        }}
        return captures;
    }}

    public static Object parseObject(@NotNull Object value, Class<?> targetClass) {{
        if (targetClass.equals(String.class) || targetClass.equals(Character.class)) {{
            return String.valueOf(value);
        }}
        if (targetClass.equals(UUID.class)) {{
            return UUID.fromString((String) value);
        }}
        if (targetClass.equals(Boolean.class)) {{
            return Boolean.valueOf((Boolean) value);
        }}
        if (targetClass.equals(Integer.class)) {{
            return Integer.valueOf((String) value);
        }}
        if (targetClass.equals(Long.class)) {{
            return Long.valueOf((String) value);
        }}
        if (targetClass.equals(Double.class)) {{
            return Double.valueOf((String) value);
        }}
        if (targetClass.equals(BigInteger.class)) {{
            return BigInteger.valueOf((Long) value);
        }}
        if (targetClass.equals(BigDecimal.class)) {{
            return BigDecimal.valueOf((Long) value);
        }}
        if (targetClass.equals(LocalDateTime.class)) {{
            String useValue = ((String) value).contains("T") ? (String) value : ((String) value) + "T00:00:00";
            return LocalDateTime.parse(useValue);
        }}

        return value;
    }}

}}
"""
    write_to_file(contents = common_utils, path_full = f'src/utils/CommonUtils.java')
    
    
    password_utils = f"""\
package {package_prefix}.utils;


import org.mindrot.jbcrypt.BCrypt;

public class PasswordUtils {{

    // Hash a password using bcrypt
    public static String hashPassword(String password) {{
        // The log rounds are 12 by default in bcrypt, but you can specify your own (e.g. 10, 12, 14).
        return BCrypt.hashpw(password, BCrypt.gensalt(12));
    }}

    // Check if the plain text password matches the hashed password
    public static boolean checkPassword(String password, String hashedPassword) {{
        return BCrypt.checkpw(password, hashedPassword);
    }}

}}
"""
    write_to_file(contents = password_utils, path_full = f'src/utils/PasswordUtils.java')
    
    ### JWT Configs
    
    jwt_auth_aspect = f"""\
package {package_prefix}.configs.jwt;
    

import {package_prefix}.configs.jwt.JwtAuthorized;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import java.lang.reflect.Method;

@Aspect
@Component
public class JwtAuthorizedAspect {{

    // Intercept request/controller methods annotated with @JwtAuthorized
    @Before("@annotation({package_prefix}.configs.jwt.JwtAuthorized)")
    public void extractAuthenticationToken(JoinPoint joinPoint) {{
        // Retrieve the authentication token from the SecurityContextHolder
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        boolean isAuthorized = authentication != null && authentication.isAuthenticated();

        // Get the method being called
        Method method = ((MethodSignature) joinPoint.getSignature()).getMethod();
        // Check if the method has the CustomAuth annotation
        JwtAuthorized jwtAuthorized = method.getAnnotation(JwtAuthorized.class);

        boolean shouldThrowError = jwtAuthorized != null && (!isAuthorized && !jwtAuthorized.suppressError());
        if (shouldThrowError) {{
            throw new RuntimeException("Not JWT Authorized");
        }}
    }}

}}
"""
    write_to_file(contents = jwt_auth_aspect, path_full = f'src/configs/jwt/JwtAuthorizedAspect.java')

    
    jwt_auth_request_filter = f"""\
package {package_prefix}.configs.jwt;
    

import {package_prefix}.configs.jwt.JwtUtilsConfig;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;

import java.io.IOException;
import java.util.List;
import java.util.UUID;


public class JwtAuthRequestFilter extends OncePerRequestFilter {{

    private JwtUtilsConfig jwtUtilsConfig;

    public JwtAuthRequestFilter(JwtUtilsConfig jwtUtilsConfig) {{
        this.jwtUtilsConfig = jwtUtilsConfig;
    }}

    @Override
    protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain filterChain
    ) throws ServletException, IOException {{
        // Get JWT token from the request header
        String token = request.getHeader("Authorization");

        // Check if token is valid
        boolean isBearerToken = token != null && token.startsWith("Bearer ");
        if (isBearerToken) {{
            token = token.substring(7); // Remove "Bearer " prefix
            try {{
                String userId = this.jwtUtilsConfig.verifyToken(token);
                SimpleGrantedAuthority authority = new SimpleGrantedAuthority("AUTH_USER");
                UsernamePasswordAuthenticationToken authenticationToken = new UsernamePasswordAuthenticationToken(userId, null, List.of(authority)); // You could add authorities here
                SecurityContextHolder.getContext().setAuthentication(authenticationToken);

                request.setAttribute("JWT", token);
                request.setAttribute("AUTH_USER_ID", UUID.fromString(userId));

                System.out.println("[JwtAuthRequestFilter] request jwt authorized");
            }}
            catch (Exception ex) {{
                // not jwt authorized
                System.out.println("[JwtAuthRequestFilter] request jwt authorization failed");
                System.out.println(ex.getMessage());
                ex.printStackTrace();
            }}
        }}

        filterChain.doFilter(request, response);
    }}
}}
"""
    write_to_file(contents = jwt_auth_request_filter, path_full = f'src/configs/jwt/JwtAuthRequestFilter.java')
    
    
    jwt_auth_method_annotation = f"""\
package {package_prefix}.configs.jwt;
    

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface JwtAuthorized {{

    boolean suppressError() default false;

}}
"""
    write_to_file(contents = jwt_auth_method_annotation, path_full = f'src/configs/jwt/JwtAuthorized.java')
    
    
    jwt_utils_config = f"""\
package {package_prefix}.configs.jwt;
    


import io.jsonwebtoken.*;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

@Component
public class JwtUtilsConfig {{

    // Secret key for signing the JWT
    private final String SECRET_KEY;  // Keep this safe!

    // Expiration time in milliseconds (e.g., 1 hour)
    private final long EXPIRATION_TIME = (1000 * 60 * 60 * 24 * 7);  // 1 week

    public JwtUtilsConfig(@Value("${{auth.jwt.secret}}") String authJwtSecret) {{
        this.SECRET_KEY = authJwtSecret;
    }}

    // Create a JWT token
    public String createToken(String userId) {{
        return Jwts.builder()
            .claims(Map.ofEntries(
                Map.entry("userId", userId)
            ))
            .subject(userId)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + this.EXPIRATION_TIME))
            .signWith(createSigningKey())
            .compact();  // Return the JWT string
    }}

    public String verifyToken(String token) {{
        try {{
            Jws<Claims> claimsJws = Jwts.parser()
                .verifyWith(this.createSigningKey())
                .build()
                .parseSignedClaims(token);

            return claimsJws.getPayload().getSubject();
        }} catch (JwtException | IllegalArgumentException e) {{
            // Handle token errors (expired, invalid, etc.)
            System.out.println("Token verification failed: " + e.getMessage());
            throw e;
        }}
    }}

    // Check if a token is expired
    public boolean isTokenExpired(String token) {{
        try {{
            Jws<Claims> claimsJws = Jwts.parser()
                .verifyWith(this.createSigningKey())
                .build()
                .parseSignedClaims(token);

            Date expirationDate = claimsJws.getPayload().getExpiration();
            return expirationDate.before(new Date());
        }} catch (JwtException | IllegalArgumentException e) {{
            return true;  // If token is invalid or expired
        }}
    }}

    // Helper method to create the signing key
    private SecretKey createSigningKey() {{
        SecretKey key = Keys.hmacShaKeyFor(this.SECRET_KEY.getBytes(StandardCharsets.UTF_8));
        return key;
    }}
}}
"""
    write_to_file(contents = jwt_utils_config, path_full = f'src/configs/jwt/JwtUtilsConfig.java')
    
    
    security_config = f"""\
package {package_prefix}.configs;
    

import {package_prefix}.configs.jwt.JwtAuthRequestFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;



@Configuration
@EnableWebSecurity
public class SecurityConfig {{

    private JwtUtilsConfig jwtUtilsConfig;

    public SecurityConfig(JwtUtilsConfig jwtUtilsConfig) {{
        this.jwtUtilsConfig = jwtUtilsConfig;
    }}

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {{
        http
            .authorizeHttpRequests(authorize -> authorize
                .requestMatchers("/").permitAll()
                .anyRequest().permitAll()
            )
            .addFilterBefore(new JwtAuthRequestFilter(this.jwtUtilsConfig), UsernamePasswordAuthenticationFilter.class)
            .csrf(AbstractHttpConfigurer::disable)
            .httpBasic(AbstractHttpConfigurer::disable)
            .formLogin(AbstractHttpConfigurer::disable);
        return http.build();
    }}
}}
"""
    write_to_file(contents = security_config, path_full = f'src/configs/SecurityConfig.java')
    
    
    domain_exception = f"""\
package {package_prefix}.exceptions;

import {package_prefix}.interfaces.ErrorCode;
import org.springframework.http.HttpStatus;
import lombok.Getter;

public class DomainException extends Exception {{
  
    @Getter
    private HttpStatus httpStatus;
    
    @Getter
    private ErrorCode errorCode;
    
    public DomainException(String message) {{
        super(message);
    }}
    
    public DomainException(String message, Throwable cause) {{
        super(message, cause);
    }}
    
    public DomainException(Throwable cause) {{
        super(cause);
    }}
    
    public DomainException(String message, HttpStatus httpStatus, ErrorCode errorCode) {{
        super(message);
        this.httpStatus = httpStatus;
        this.errorCode = errorCode;
    }}
    
    public DomainException(String message, Throwable cause, HttpStatus httpStatus, ErrorCode errorCode) {{
        super(message, cause);
        this.httpStatus = httpStatus;
        this.errorCode = errorCode;
    }}
    
    public DomainException(Throwable cause, HttpStatus httpStatus, ErrorCode errorCode) {{
        super(cause);
        this.httpStatus = httpStatus;
        this.errorCode = errorCode;
    }}

}}
"""
    write_to_file(contents = domain_exception, path_full = f'src/exceptions/DomainException.java')
    
    
    domain_runtime_exception = f"""\
package {package_prefix}.exceptions;

import org.springframework.http.HttpStatus;
import lombok.Getter;

public class DomainRuntimeException extends RuntimeException {{
  
    @Getter
    private HttpStatus httpStatus;
    
    @Getter
    private ErrorCode errorCode;
    
    public DomainRuntimeException(String message) {{
        super(message);
    }}
    
    public DomainRuntimeException(String message, Throwable cause) {{
        super(message, cause);
    }}
    
    public DomainRuntimeException(Throwable cause) {{
        super(cause);
    }}
    
    public DomainRuntimeException(String message, HttpStatus httpStatus, ErrorCode errorCode) {{
        super(message);
        this.httpStatus = httpStatus;
        this.errorCode = errorCode;
    }}
    
    public DomainRuntimeException(String message, Throwable cause, HttpStatus httpStatus, ErrorCode errorCode) {{
        super(message, cause);
        this.httpStatus = httpStatus;
        this.errorCode = errorCode;
    }}
    
    public DomainRuntimeException(Throwable cause, HttpStatus httpStatus, ErrorCode errorCode) {{
        super(cause);
        this.httpStatus = httpStatus;
        this.errorCode = errorCode;
    }}

}}
"""
    write_to_file(contents = domain_runtime_exception, path_full = f'src/exceptions/DomainRuntimeException.java')
    

    error_codes_interface = f"""\
package {package_prefix}.interfaces;

public interface ErrorCode {{
  
  Integer errorCode = null;
  String errorClass = null;
  String errorMessage = null;

}}
"""
    write_to_file(contents = error_codes_interface, path_full = f'src/interfaces/ErrorCode.java')
    
    request_params_utils = f"""\
package {package_prefix}.utils;

import {package_prefix}.annotations.IgnoreOnSearch;
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Root;
import org.springframework.data.jpa.domain.Specification;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.time.LocalDateTime;
import java.util.*;

import jakarta.persistence.criteria.Predicate;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


/*

    Examples:
    ===

    /search?query=or<and<query<id|eq|4799afa3-bd39-415d-a024-65d8afa7acc6>,query<createdAtUtc|lte|2025-03-01>>,and<query<bio|ilike|helloworld>,query<headline|like|great>>,and<query<city|ilike|plano>>,and<query<state|ilike|texas>>>

    /search?id=eq|{{id}}
    /search?createdAtUtc=lte|{{createdAtUtc}}
    /search?bio=ilike|{{bio}}&headline=ilike|{{value}}&_or=true

*/

public class RequestParamsUtils {{

    @FunctionalInterface
    private interface FieldOpFn <T> {{
        Predicate fn(Root<T> root, CriteriaQuery<?> query, CriteriaBuilder cb, String field, String op, Object value);
    }}

    public static final Map<Class<?>, Set<String>> ACCEPTED_OPS_BY_DATATYPE = Map.ofEntries(
        Map.entry(String.class, Set.of("eq", "ne", "isNull", "isNotNull", "like", "ilike", "notLike", "notILike", "startsWith", "endsWith", "regexp", "notRegexp", "iregexp", "notIRegexp", "any", "in", "notIn")),
        Map.entry(UUID.class, Set.of("eq", "ne", "isNull", "isNotNull", "like", "ilike", "notLike", "notILike", "startsWith", "endsWith", "regexp", "notRegexp", "iregexp", "notIRegexp", "any", "in", "notIn")),
        Map.entry(Character.class, Set.of("eq", "ne", "isNull", "isNotNull", "like", "ilike", "notLike", "notILike", "startsWith", "endsWith", "regexp", "notRegexp", "iregexp", "notIRegexp", "any", "in", "notIn")),
        Map.entry(Boolean.class, Set.of("eq", "ne", "isNull", "isNotNull", "isTrue", "isFalse")),
        Map.entry(Integer.class, Set.of("eq", "ne", "isNull", "isNotNull", "lt", "lte", "gt", "gte", "in", "notIn", "any", "between", "notBetween")),
        Map.entry(Long.class, Set.of("eq", "ne", "isNull", "isNotNull", "lt", "lte", "gt", "gte", "in", "notIn", "any", "between", "notBetween")),
        Map.entry(Double.class, Set.of("eq", "ne", "isNull", "isNotNull", "lt", "lte", "gt", "gte", "in", "notIn", "any", "between", "notBetween")),
        Map.entry(BigInteger.class, Set.of("eq", "ne", "isNull", "isNotNull", "lt", "lte", "gt", "gte", "in", "notIn", "any", "between", "notBetween")),
        Map.entry(BigDecimal.class, Set.of("eq", "ne", "isNull", "isNotNull", "lt", "lte", "gt", "gte", "in", "notIn", "any", "between", "notBetween")),
        Map.entry(LocalDateTime.class, Set.of("eq", "ne", "isNull", "isNotNull", "lt", "lte", "gt", "gte", "in", "notIn", "any", "between", "notBetween"))
    );

    // here for reference
    public static final String OP_REGEX = "(eq|ne|isNull|isNotNull|isTrue|isFalse|or|gt|gte|lt|lte|between|notBetween|in|notIn|like|ilike|notLike|notILike|startsWith|endsWith|regexp|notRegexp|iregexp|notIRegexp|any)";

    public static final String FILED_QUERY_REGEX = "([a-z]+)\\|([\\w\\-\\s,\\|]+)";
    public static final String NON_VALUE_QUERY_REGEX = "(isNull|isNotNull|isTrue|isFalse)";
    public static final String SINGLE_QUERY_REGEX = "query<([\\w\\-]+)\\|([a-z]+)\\|([\\w\\-\\s,\\|]+)>";
    public static final String ANDLIST_REGEX = "and<((,?query<([\\w\\-]+)\\|([a-z]+)\\|([\\w\\-\\s,\\|]+)>)*)>";
    public static final String GLOBAL_OR_REGEX = "^or<(,?and<((,?query<([\\w\\-]+)\\|([a-z]+)\\|([\\w\\-\\s,\\|]+)>)*)>)*>$";

    public static final Pattern FILED_QUERY_REGEX_PATTERN = Pattern.compile(FILED_QUERY_REGEX);
    public static final Pattern NON_VALUE_QUERY_REGEX_PATTERN = Pattern.compile(NON_VALUE_QUERY_REGEX);
    public static final Pattern SINGLE_QUERY_REGEX_PATTERN = Pattern.compile(SINGLE_QUERY_REGEX);
    public static final Pattern ANDLIST_REGEX_PATTERN = Pattern.compile(ANDLIST_REGEX);

    public static <T> Specification<T> convertParamsToSearchPredicates(Map<String, String> queryParams, Class<? extends T> entity) {{
        // if "query" param was given, prefer processing that
        // else, process query params as separate field predicates
        String query = queryParams.getOrDefault("query", null);
        boolean isQueryStringFormat = (query != null && query.matches(RequestParamsUtils.GLOBAL_OR_REGEX));
        return isQueryStringFormat
            ? RequestParamsUtils.handleQueryStringParam(queryParams, entity)
            : RequestParamsUtils.handleFieldsQueryParams(queryParams, entity);
    }}


    public static <T> Specification<T> handleFieldsQueryParams(Map<String, String> queryParams, Class<? extends T> entity) {{
        List<Specification<T>> andSpecs = new ArrayList<>();

        Map<String, Class<?>> entityClassFieldDefs = CommonUtils.getClassFieldNamesAndTypes(entity);

        for (String fieldName : queryParams.keySet()) {{
            Matcher singleQueryMatcher = RequestParamsUtils.FILED_QUERY_REGEX_PATTERN.matcher(queryParams.get(fieldName));
            if (singleQueryMatcher.find()) {{
                String queryOp = singleQueryMatcher.group(1);
                String queryValue = singleQueryMatcher.group(2);
                Specification<T> spec = RequestParamsUtils.buildPredicate(entityClassFieldDefs, entity, fieldName, queryOp, queryValue);
                andSpecs.add(spec);
            }}
            Matcher nonValueMatcher = RequestParamsUtils.NON_VALUE_QUERY_REGEX_PATTERN.matcher(queryParams.get(fieldName));
            if (nonValueMatcher.find()) {{
                String queryOp = nonValueMatcher.group(1);
                Specification<T> spec = RequestParamsUtils.buildPredicate(entityClassFieldDefs, entity, fieldName, queryOp, null);
                andSpecs.add(spec);
            }}
        }}

        return (root, query, cb) -> {{
            boolean useOrWhereClause = queryParams.containsKey("_or") && queryParams.get("_or").equalsIgnoreCase("true");
            List<Predicate> predicateList = andSpecs.stream().map(spec -> spec.toPredicate(root, query, cb)).toList();
            return useOrWhereClause
                ? cb.or(predicateList.toArray(new Predicate[0]))
                : cb.and(predicateList.toArray(new Predicate[0]));
        }};
    }}

    public static <T> Specification<T> handleQueryStringParam(Map<String, String> queryParams, Class<? extends T> entity) {{
        List<Specification<T>> andSpecs = new ArrayList<>();

        Map<String, Class<?>> entityClassFieldDefs = CommonUtils.getClassFieldNamesAndTypes(entity);

        Matcher andListQueryMatcher = RequestParamsUtils.ANDLIST_REGEX_PATTERN.matcher(queryParams.get("query"));
        List<String> andListCaptures = CommonUtils.getAllCapturesFromMatcher(andListQueryMatcher);

        for (String andListCapture : andListCaptures) {{
            Matcher singleQueryMatcher = RequestParamsUtils.SINGLE_QUERY_REGEX_PATTERN.matcher(andListCapture);
            List<Specification<T>> specs = new ArrayList<>();
            while (singleQueryMatcher.find()) {{
                String queryField = singleQueryMatcher.group(1);
                String queryOp = singleQueryMatcher.group(2);
                Object queryValue = singleQueryMatcher.group(3);
                Specification<T> spec = RequestParamsUtils.buildPredicate(entityClassFieldDefs, entity, queryField, queryOp, queryValue);
                specs.add(spec);
            }}
            Specification<T> specification = null;
            for (Specification<T> s : specs) {{
                if (specification == null) {{
                    specification = s;
                }}
                else {{
                    specification.and(s);
                }}
            }}
            if (specification != null) {{
                andSpecs.add(specification);
            }}
        }}

        return (root, query, cb) -> {{
            List<Predicate> predicateList = andSpecs.stream().map(spec -> spec.toPredicate(root, query, cb)).toList();
            return cb.or(predicateList.toArray(new Predicate[0]));
        }};
    }}

    public static <T> Specification<T> buildPredicate(Map<String, Class<?>> entityClassFieldDefs, Class<?> entity, String fieldName, String op, Object fieldValue) {{
        Class<?> fieldType = entityClassFieldDefs.getOrDefault(fieldName, null);
        if (fieldType == null) {{
            return (root, query1, cb) -> cb.conjunction();
        }}
        boolean isAcceptedOpForType = (
            RequestParamsUtils.ACCEPTED_OPS_BY_DATATYPE.containsKey(fieldType)
            && RequestParamsUtils.ACCEPTED_OPS_BY_DATATYPE.get(fieldType).contains(op)
        );
        if (!isAcceptedOpForType) {{
            return (root, query1, cb) -> cb.conjunction();
        }}
        try {{
            boolean hasIgnoreAnnotation = entity.getDeclaredField(fieldName).isAnnotationPresent(IgnoreOnSearch.class);
            if (hasIgnoreAnnotation) {{
                return (root, query1, cb) -> cb.conjunction();
            }}
        }}
        catch (NoSuchFieldException ex) {{
            return (root, query1, cb) -> cb.conjunction();
        }}

        return (Root<T> root, CriteriaQuery<?> query1, CriteriaBuilder cb) -> {{
            FieldOpFn<T> fieldOpFn = RequestParamsUtils.makeQueryBuilder();
            if (fieldValue == null) {{
                return fieldOpFn.fn(root, query1, cb, fieldName, op, null);
            }}

            String valueAsString = String.valueOf(fieldValue);
            Object useValue;
            if (valueAsString.contains(",")) {{
                // is comma-separated list
                List<Object> list = new ArrayList<>();
                for (String v : valueAsString.split(",")) {{
                    list.add(CommonUtils.parseObject(v, fieldType));
                }}
                useValue = list;
            }}
            else {{
                useValue = CommonUtils.parseObject(fieldValue, fieldType);
            }}

            return fieldOpFn.fn(root, query1, cb, fieldName, op, useValue);
        }};
    }}

    public static <T> FieldOpFn<T> makeQueryBuilder() {{
        return (Root<T> root, CriteriaQuery<?> query, CriteriaBuilder cb, String field, String operator, Object queryValue) -> {{
            return switch (operator) {{
                case "eq" -> cb.equal(root.get(field), queryValue);
                case "ne" -> cb.notEqual(root.get(field), queryValue);
                case "isNull" -> cb.isNull(root.get(field));
                case "isNotNull" -> cb.isNotNull(root.get(field));
                case "isTrue" -> cb.isTrue(root.get(field));
                case "isFalse" -> cb.isFalse(root.get(field));
                case "gt" -> cb.greaterThan(root.get(field), (Comparable) queryValue);
                case "gte" -> cb.greaterThanOrEqualTo(root.get(field), (Comparable) queryValue);
                case "lt" -> cb.lessThan(root.get(field), (Comparable) queryValue);
                case "lte" -> cb.lessThanOrEqualTo(root.get(field), (Comparable) queryValue);
                case "between" -> cb.between(root.get(field), (Comparable) ((List<?>) queryValue).get(0), (Comparable) ((List<?>) queryValue).get(1));
                case "notBetween" -> cb.between(root.get(field), (Comparable) ((List<?>) queryValue).get(0), (Comparable) ((List<?>) queryValue).get(1)).not();
                case "in" -> cb.in(root.get(field)).value(queryValue);
                case "notIn" -> cb.not(root.get(field)).in(queryValue);
                case "like" -> cb.like(root.get(field), "%" + queryValue + "%");
                case "ilike" -> cb.like(cb.lower(root.get(field)), "%" + String.valueOf(queryValue).toLowerCase() + "%");
                case "notLike" -> cb.notLike(root.get(field), "%" + queryValue + "%");
                case "notILike" -> cb.notLike(cb.lower(root.get(field)), "%" + String.valueOf(queryValue).toLowerCase() + "%");
                case "startsWith" -> cb.like(root.get(field), queryValue + "%");
                case "endsWith" -> cb.like(root.get(field), "%" + queryValue);
                case "regexp" -> cb.like(root.get(field), queryValue.toString());
                case "notRegexp" -> cb.notLike(root.get(field), queryValue.toString());
                case "iregexp" -> cb.like(cb.lower(root.get(field)), queryValue.toString());
                case "notIRegexp" -> cb.notLike(cb.lower(root.get(field)), queryValue.toString());

                default -> cb.conjunction();
            }};
        }};
    }}

}}
"""
    write_to_file(contents = request_params_utils, path_full = f'src/utils/RequestParamsUtils.java')
    
    ignore_on_search_annotation = f"""\
package {package_prefix}.annotations;


import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface IgnoreOnSearch {{
}}
"""
    write_to_file(contents = ignore_on_search_annotation, path_full = f'src/annotations/IgnoreOnSearch.java')
    
    
    app_javas = f"""\
package {package_prefix};


import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = {{ "{package_prefix}" }})
public class App {{

    public static void main(String[] args) {{
        SpringApplication.run(App.class, args);
    }}

}}
"""
    write_to_file(contents = app_javas, path_full = f'src/App.java')
    
    
    auth_controller = f"""\
package {package_prefix}.controllers;

import org.springframework.web.bind.annotation.*;
import {package_prefix}.configs.jwt.JwtAuthorized;
import {package_prefix}.services.interfaces.AuthService;
import {package_prefix}.domain.dto.AuthResponseDto;
import {package_prefix}.domain.requests.LoginUserPayload;
import {package_prefix}.domain.requests.SignupUserPayload;



@RestController
@RequestMapping("/auth")
public class AuthController {{
  
    private final AuthService authService;
    
    public AuthController(AuthService authService) {{
      this.authService = authService;
    }}
    
    
    @GetMapping(value = "/refresh")
    public DataResponse<AuthResponseDto> refreshJwtToken(@RequestAttribute("JWT") String jwt) {{
        return new DataResponse<>(this.authService.refreshJwtToken(jwt));
    }}

    @GetMapping(value = "/parse")
    public DataResponse<AuthResponseDto> parseJwtToken(@RequestAttribute("JWT") String jwt) {{
        return new DataResponse<>(this.authService.parseJwtToken(jwt));
    }}
    
    @PostMapping(value = "")
    public DataResponse<AuthResponseDto> signupUser(@RequestBody SignupUserPayload payload) {{
        return new DataResponse<>(this.authService.signupUser(payload));
    }}

    @PutMapping(value = "")
    public DataResponse<AuthResponseDto> loginUser(@RequestBody LoginUserPayload payload) {{
        return new DataResponse<>(this.authService.loginUser(payload));
    }}
  
}}
"""
    write_to_file(contents = auth_controller, path_full = f'src/controllers/AuthController.java')
    
    
    auth_service = f"""\
package {package_prefix}.services.interfaces;

import {package_prefix}.domain.dto.AuthResponseDto;
import {package_prefix}.domain.requests.LoginUserPayload;
import {package_prefix}.domain.requests.SignupUserPayload;


public interface AuthService {{
  
    AuthResponseDto signupUser(SignupUserPayload payload);
    
    AuthResponseDto loginUser(LoginUserPayload payload);
    
    AuthResponseDto refreshJwtToken(String jwt);
    
    AuthResponseDto parseJwtToken(String jwt);
    
}}
"""
    write_to_file(contents = auth_service, path_full = f'src/services/interfaces/AuthService.java')
    
    
    auth_service_impl = f"""\
package {package_prefix}.services.implementations;

import {package_prefix}.configs.jwt.JwtUtilsConfig;
import {package_prefix}.domain.dto.AuthResponseDto;
import {package_prefix}.domain.requests.LoginUserPayload;
import {package_prefix}.domain.requests.SignupUserPayload;
import {package_prefix}.services.interfaces.AuthService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;


@Service
public class AuthServiceImpl implements AuthService {{
  
    private final JwtUtilsConfig jwtUtilsConfig;
    
    public AuthServiceImpl(JwtUtilsConfig jwtUtilsConfig) {{
        this.jwtUtilsConfig = jwtUtilsConfig;
    }}
    
    @Override
    @Transactional
    public AuthResponseDto signupUser(SignupUserPayload payload) {{
        // TODO: implement signupUser
        return new AuthResponseDto();
    }}
    
    @Override
    @Transactional
    public AuthResponseDto loginUser(LoginUserPayload payload) {{
        // TODO: implement signupUser
        return new AuthResponseDto();
    }}
    
    
    @Override
    public AuthResponseDto refreshJwtToken(String jwt) {{
        try {{
            String userId = this.jwtUtilsConfig.verifyToken(jwt);
            // TODO: implement refreshJwtToken
            return new AuthResponseDto();
        }}
        catch (Exception ex) {{
            throw new RuntimeException(String.format("Could not verify JWT: %s", jwt), ex);
        }}
    }}
    
    @Override
    @Transactional
    public AuthResponseDto parseJwtToken(String jwt) {{
        try {{
            String userId = this.jwtUtilsConfig.verifyToken(jwt);
            // TODO: implement refreshJwtToken
            return new AuthResponseDto();
        }}
        catch (Exception ex) {{
            throw new RuntimeException(String.format("Could not verify JWT: %s", jwt), ex);
        }}
    }}
      
}}
"""
    write_to_file(contents = auth_service_impl, path_full = f'src/services/implementations/AuthServiceImpl.java')
    
    
    auth_response_dto = f"""\
package {package_prefix}.domain.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;


@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class AuthResponseDto {{
  
    private String jwt;
    private String refreshToken;
    private String userId;
    // TODO: add more fields as needed
    
}}
"""
    write_to_file(contents = auth_response_dto, path_full = f'src/domain/dto/AuthResponseDto.java')
    
    
    login_user_payload = f"""\
package {package_prefix}.domain.requests;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;


@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class LoginUserPayload {{
  
    private String email;
    private String password;
    
}}
"""
    write_to_file(contents = login_user_payload, path_full = f'src/domain/requests/LoginUserPayload.java')
    
    
    signup_user_payload = f"""\
package {package_prefix}.domain.requests;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;


@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class SignupUserPayload {{
  
    private String email;
    private String password;
    // TODO: add more fields as needed
    
}}
"""
    write_to_file(contents = signup_user_payload, path_full = f'src/domain/requests/SignupUserPayload.java')
    
    
    
    
    


if __name__ == "__main__":
    """
    NOTE: assumptions are made about the SQL file format.
    1. the database is Postgres
    2. tables have a {schema.table} format
    
    SQL file table definitions are expected to be in the following format:
    
    CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
        {column_name} {data_type in UPPERCASE} NOT NULL etc...,
    );
    
    Example:
    
    CREATE TABLE IF NOT EXISTS schema.users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        metadata JSONB DEFAULT NULL,
        created_at_utc TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at_utc TIMESTAMP DEFAULT NULL,
        deleted_at_utc TIMESTAMP DEFAULT NULL
    );
    """
    
    app_package_prefix = f"<enter_app_package>"
  
    sql_configs = [
      # format: { "service": "service_name", "sql_path": "full/path/to/sql_file.sql" }
      { "service": "myah", "sql_path": "/Users/ryanwaite/Desktop/sql-projects/myah/sql/app/ddl/app.v1.sql" }
    ]
    
    if os.path.exists("src"):
      shutil.rmtree("src")
      
      
    create_helper_classes(app_package_prefix)
    
    main_services_enum = generate_main_services_enum([ c['service'] for c in sql_configs ], app_package_prefix)
    write_to_file(contents = main_services_enum, path_full = f'src/enums/ServiceNames.java')
      
    for sql_config in sql_configs:
      # print("processing: ", sql_configs)
      
      results = parse_sql_file(sql_config, app_package_prefix)
      
      use_service_name = make_class_name(sql_config['service'], False)
      
      write_items_to_files(items = results['entities'], classNameSuffix = "Entity", output_dir = f'src/datasources/{sql_config['service']}/entities')
      write_items_to_files(items = results['dto'], classNameSuffix = "Dto", output_dir = f'src/datasources/{sql_config['service']}/dto')
      write_items_to_files(items = results['typescript_types_classes'], makeFileName = lambda n: f"{singularize_word(n)}.types.ts", output_dir = f'src/datasources/{sql_config['service']}/typescript')
      write_items_to_files(items = results['repositories'], classNameSuffix = "Repository", output_dir = f'src/datasources/{sql_config['service']}/repositories')
      write_items_to_files(items = results['controllers'], classNameSuffix = "Controller", output_dir = f'src/datasources/{sql_config['service']}/controllers')
      write_items_to_files(items = results['service_interfaces'], classNameSuffix = "Service", output_dir = f'src/datasources/{sql_config['service']}/services/interfaces')
      write_items_to_files(items = results['service_implementations'], classNameSuffix = "ServiceImpl", output_dir = f'src/datasources/{sql_config['service']}/services/implementations')
      write_items_to_files(items = results['search_params'], classNameSuffix = "SearchParams", output_dir = f'src/datasources/{sql_config['service']}/dto/searches')
      write_items_to_files(items = results['model_event_enums'], classNameSuffix = "ModelEvents", output_dir = f'src/datasources/{sql_config['service']}/enums/modelevents')
      write_items_to_files(items = results['not_found_exceptions'], classNameSuffix = "NotFoundException", output_dir = f'src/datasources/{sql_config['service']}/exceptions')
      write_items_to_files(items = results['invalid_data_exceptions'], classNameSuffix = "InvalidDataException", output_dir = f'src/datasources/{sql_config['service']}/exceptions')
      write_items_to_files(items = results['processing_exceptions'], classNameSuffix = "ProcessingException", output_dir = f'src/datasources/{sql_config['service']}/exceptions')
      write_items_to_files(items = results['error_codes'], classNameSuffix = "ErrorCodes", output_dir = f'src/datasources/{sql_config['service']}/enums/errorcodes')
      
      write_to_file(contents = results['main_datasource_config'], path_full = f'src/configs/DatasourceJpaConfig{use_service_name}Db.java')
      write_to_file(contents = results['main_service_interface'], path_full = f'src/services/interfaces/{use_service_name}Service.java')
      write_to_file(contents = results['main_service_implementation'], path_full = f'src/services/implementations/{use_service_name}ServiceImpl.java')
      write_to_file(contents = results['main_controller'], path_full = f'src/controllers/{use_service_name}Controller.java')
      write_to_file(contents = results['model_names_enum'], path_full = f'src/datasources/{sql_config['service']}/enums/{use_service_name}ModelNames.java')
      write_to_file(contents = results['main_controller_advice'], path_full = f'src/controllers/advices/AppControllerAdvice.java')
      
    # END for
      
    print("Resource classes generated successfully")