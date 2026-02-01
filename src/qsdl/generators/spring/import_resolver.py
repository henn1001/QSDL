# Copyright 2026 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Spring Generator Java import resolver"""

from qsdl import dsl
from qsdl.generators.spring.config import Database

from . import models as spring
from . import util


def resolve_dynamic_imports() -> None:
    """resolve all model related dynamic imports"""

    namespaced_packages = {}

    for model in util.Store.models:
        if model.package._namespace not in namespaced_packages:
            namespaced_packages[model.package._namespace] = model.package

    util.Store.packages = list(namespaced_packages.values())


def generate_imports_for_template(
    template_name: str, api_or_model: spring.ApiClass | spring.ModelClass | None
) -> list[str]:
    api_class: spring.ApiClass | None = None
    model_class: spring.ModelClass | None = None

    if api_or_model and isinstance(api_or_model, spring.ApiClass):
        api_class = api_or_model
    if api_or_model and isinstance(api_or_model, spring.ModelClass):
        model_class = api_or_model

    # helpers
    is_db = util.Store.config.database == Database.HIBERNATE

    # import definitions
    import_sets = {
        "Api.j2": [
            f"import {api_class.package.domain}.*;" if api_class else None,
            f"import {util.Store.package.model}.CursorPage;",
            f"import {util.Store.package.model}.CursorPageable;",
            *(
                [
                    f"import {util.get_model_for(op.filter_name).package.domain}.{op.filter_name};"
                    for op in api_class.operations
                    if op.uses_filter
                ]
                if api_class
                else []
            ),
            "import jakarta.json.JsonMergePatch;",
            "import java.util.List;",
            "import org.springframework.http.HttpStatus;",
            "import org.springframework.http.ResponseEntity;",
            "import org.springframework.stereotype.Controller;",
            "import org.springframework.web.bind.annotation.DeleteMapping;",
            "import org.springframework.web.bind.annotation.GetMapping;",
            "import org.springframework.web.bind.annotation.PatchMapping;",
            "import org.springframework.web.bind.annotation.PathVariable;",
            "import org.springframework.web.bind.annotation.PostMapping;",
            "import org.springframework.web.bind.annotation.PutMapping;",
            "import org.springframework.web.bind.annotation.RequestBody;",
            "import org.springframework.web.bind.annotation.RequestMapping;",
            "import tools.jackson.databind.node.ObjectNode;",
            "import java.util.List;",
        ],
        "Controller.j2": [
            f"import {api_class.package.api}.{api_class.name}Api;" if api_class else None,
            f"import {api_class.package.domain}.*;" if api_class else None,
            *(
                [
                    f"import {api_class.package.mapper}.{api_class.name}Mapper;",
                    f"import {api_class.package.service}.{api_class.name}Service;",
                ]
                if api_class and api_class.has_generated
                else []
            ),
            f"import {util.Store.package.controller}.BaseController;",
            f"import {util.Store.package.util}.JsonMergePatchUtil;",
            f"import {util.Store.package.util}.Validator;",
            f"import {util.Store.package.model}.CursorPage;",
            f"import {util.Store.package.model}.CursorPageable;",
            *(
                [
                    f"import {util.get_model_for(op.filter_name).package.domain}.{op.filter_name};"
                    for op in api_class.operations
                    if op.uses_filter
                ]
                if api_class
                else []
            ),
            "import jakarta.json.JsonMergePatch;",
            "import org.springframework.http.HttpStatus;",
            "import org.springframework.http.ResponseEntity;",
            "import org.springframework.stereotype.Controller;",
            "import org.springframework.web.bind.annotation.DeleteMapping;",
            "import org.springframework.web.bind.annotation.GetMapping;",
            "import org.springframework.web.bind.annotation.PatchMapping;",
            "import org.springframework.web.bind.annotation.PathVariable;",
            "import org.springframework.web.bind.annotation.PostMapping;",
            "import org.springframework.web.bind.annotation.PutMapping;",
            "import org.springframework.web.bind.annotation.RequestBody;",
            "import org.springframework.web.bind.annotation.RequestMapping;",
            "import tools.jackson.databind.node.ObjectNode;",
            "import java.util.List;",
            "import lombok.AllArgsConstructor;",
        ],
        "Service.j2": [
            f"import {api_class.package.domain}.*;" if api_class else None,
            *(
                [
                    f"import {api_class.package.entity}.*;",
                    f"import {api_class.package.mapper}.*;",
                    f"import {api_class.package.repository}.*;",
                    f"import {util.Store.package.repository}.*;",
                    f"import {util.Store.package.util}.PredicateBuilder;",
                ]
                if api_class and is_db
                else []
            ),
            *(
                [
                    f"import {util.get_model_for(op.filter_name).package.domain}.{op.filter_name};"
                    for op in api_class.operations
                    if op.uses_filter and util.get_model_for(op.filter_name).package.domain != api_class.package.domain
                ]
                if api_class
                else []
            ),
            *(
                [
                    *[f"import {parent.model.package.domain}.*;" for parent in api_class.model.parents],
                    *[f"import {parent.model.package.entity}.*;" for parent in api_class.model.parents],
                    *[f"import {parent.model.package.mapper}.*;" for parent in api_class.model.parents],
                    *[f"import {parent.model.package.repository}.*;" for parent in api_class.model.parents],
                ]
                if api_class and is_db and api_class.model
                else []
            ),
            f"import {util.Store.package.enum}.*;",
            f"import {util.Store.package.model}.CursorPage;",
            f"import {util.Store.package.model}.CursorPageable;",
            f"import {util.Store.package.exception}.AppException;",
            f"import {util.Store.package.exception}.AppExceptionUtil;",
            "import lombok.AllArgsConstructor;",
            "import lombok.extern.slf4j.Slf4j;",
            "import org.springframework.stereotype.Service;",
            "import org.springframework.transaction.annotation.Transactional;",
            "import java.util.Arrays;",
        ],
        "Entity.j2": [
            # Enum imports
            *(
                [
                    f"import {util.Store.package.enum}.{field.type};"
                    for field in model_class.entity_fields
                    if field.is_enum
                ]
                if model_class
                else []
            ),
            # Nested entity imports (including relations)
            *(
                [
                    f"import {util.get_model_for(field.type).package.entity}.{util.get_model_for(field.type).name}Entity;"
                    for field in model_class.entity_fields
                    if field.is_object and util.get_model_for(field.type).package.entity != model_class.package.entity
                ]
                if model_class
                else []
            ),
            # Nested base imports
            # import if base is not in same package as entity
            *(
                [
                    f"import {util.get_model_for(field.type).package.domain}.{field.type};"
                    for field in model_class.entity_fields
                    if field.is_base and util.get_model_for(field.type).package.domain != model_class.package.entity
                ]
                if model_class
                else []
            ),
            f"import {util.Store.package.model}.AbstractPersistentBase;",
            f"import {util.Store.package.model}.AbstractPersistentObject;",
            "import com.fasterxml.jackson.annotation.JsonIgnore;",
            "import tools.jackson.databind.node.ObjectNode;",
            "import org.hibernate.annotations.JdbcTypeCode;",
            "import org.hibernate.type.SqlTypes;",
            "import org.hibernate.envers.Audited;" if util.Store.config.use_auditing else None,
            "import lombok.Getter;",
            "import lombok.Setter;",
            "import jakarta.persistence.CollectionTable;",
            "import jakarta.persistence.Column;",
            "import jakarta.persistence.CascadeType;",
            "import jakarta.persistence.ElementCollection;",
            "import jakarta.persistence.Entity;",
            "import jakarta.persistence.EnumType;",
            "import jakarta.persistence.Enumerated;",
            "import jakarta.persistence.FetchType;",
            "import jakarta.persistence.JoinColumn;",
            "import jakarta.persistence.JoinTable;",
            "import jakarta.persistence.OneToOne;",
            "import jakarta.persistence.OneToMany;",
            "import jakarta.persistence.ManyToMany;",
            "import jakarta.persistence.ManyToOne;",
            "import jakarta.persistence.PreRemove;",
            "import jakarta.persistence.Table;",
            "import jakarta.validation.constraints.NotNull;",
            "import java.time.LocalDate;",
            "import java.time.OffsetDateTime;",
            "import java.util.LinkedHashSet;",
            "import java.util.Set;",
            "import java.util.List;",
        ],
        "Request.j2": [
            # Enum imports
            *(
                [f"import {util.Store.package.enum}.{field.type};" for field in model_class.fields if field.is_enum]
                if model_class
                else []
            ),
            # Nested entity imports for Request (non-relation, non-read-only)
            *(
                [
                    f"import {util.get_model_for(field.type).package.domain}.{util.get_model_for(field.type).name}Request;"
                    for field in model_class.fields
                    if (field.is_object or field.is_base)
                    and not field.is_relation
                    and not field.is_read_only
                    and util.get_model_for(field.type).package.domain != model_class.package.domain
                ]
                if model_class
                else []
            ),
            "import com.fasterxml.jackson.annotation.JsonProperty;",
            "import tools.jackson.databind.node.ObjectNode;",
            "import io.soabase.recordbuilder.core.RecordBuilder;",
            "import jakarta.validation.Valid;",
            "import jakarta.validation.constraints.Max;",
            "import jakarta.validation.constraints.Min;",
            "import jakarta.validation.constraints.Pattern;",
            "import jakarta.validation.constraints.NotNull;",
            "import jakarta.validation.constraints.Size;",
            "import java.time.LocalDate;",
            "import java.time.OffsetDateTime;",
            "import java.util.List;",
        ],
        "Response.j2": [
            # Enum imports
            *(
                [f"import {util.Store.package.enum}.{field.type};" for field in model_class.fields if field.is_enum]
                if model_class
                else []
            ),
            # Nested entity imports for Response (non-relation, non-write-only)
            *(
                [
                    f"import {util.get_model_for(field.type).package.domain}.{util.get_model_for(field.type).name};"
                    for field in model_class.fields
                    if (field.is_object or field.is_base)
                    and not field.is_relation
                    and not field.is_write_only
                    and util.get_model_for(field.type).package.domain != model_class.package.domain
                ]
                if model_class
                else []
            ),
            "import com.fasterxml.jackson.annotation.JsonProperty;",
            "import tools.jackson.databind.node.ObjectNode;",
            "import io.soabase.recordbuilder.core.RecordBuilder;",
            "import jakarta.validation.constraints.NotNull;",
            "import jakarta.validation.Valid;",
            "import jakarta.validation.constraints.Max;",
            "import jakarta.validation.constraints.Min;",
            "import jakarta.validation.constraints.Pattern;",
            "import jakarta.validation.constraints.Size;",
            "import java.time.LocalDate;",
            "import java.time.OffsetDateTime;",
            "import java.util.List;",
        ],
        "Mapper.j2": [
            f"import {model_class.package.domain}.{model_class.name}Request;" if model_class else None,
            f"import {model_class.package.domain}.{model_class.name};" if model_class else None,
            f"import {model_class.package.entity}.{model_class.name}Entity;" if model_class and is_db else None,
            # Opaque base type Request imports for mapper conversion methods
            *(
                [
                    f"import {model_class.package.domain}.{mapper.name}Request;"
                    for mapper in model_class.mappers
                    if isinstance(mapper, dsl.Base)
                ]
                if model_class
                else []
            ),
            # Opaque base type imports for mapper conversion methods
            *(
                [
                    f"import {model_class.package.domain}.{mapper.name};"
                    for mapper in model_class.mappers
                    if isinstance(mapper, dsl.Base)
                ]
                if model_class
                else []
            ),
            "import org.mapstruct.InheritConfiguration;",
            "import org.mapstruct.Mapper;",
            "import org.mapstruct.Mapping;",
            "import org.mapstruct.MappingTarget;",
            "import org.mapstruct.ReportingPolicy;",
        ],
        "Repository.j2": [
            f"import {model_class.package.entity}.{model_class.name}Entity;" if model_class else None,
            f"import {util.Store.package.repository}.*;"
            if model_class and model_class.package.repository != util.Store.package.repository
            else None,
            "import org.springframework.stereotype.Repository;",
            "import java.util.Optional;",
        ],
        "DControllerTest.j2": [
            # Model-specific imports
            f"import {util.Store.config.base_package}.TestConfig;",
            f"import {util.Store.config.base_package}.TestUtils;",
            f"import {util.Store.package.enum}.ErrorCode;",
            f"import {util.Store.package.util}.JsonMergePatchConverter.MediaTypeExtension;",
            f"import {util.Store.package.util}.JsonUtil;",
            f"import {util.Store.package.model}.AppError;",
            f"import {util.Store.package.model}.CursorPage;",
            f"import {model_class.package.domain}.{model_class.name}Request;" if model_class else None,
            f"import {model_class.package.domain}.{model_class.name};" if model_class else None,
            f"import {model_class.package.service}.{model_class.name}Service;" if model_class else None,
            "import static org.junit.jupiter.api.Assertions.assertEquals;",
            "import static org.mockito.ArgumentMatchers.any;",
            "import static org.mockito.ArgumentMatchers.eq;",
            "import static org.mockito.Mockito.when;",
            "import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;",
            "import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;",
            "import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;",
            "import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;",
            "import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;",
            "import java.util.Arrays;",
            "import org.json.JSONObject;",
            "import org.junit.jupiter.api.Test;",
            "import org.skyscreamer.jsonassert.JSONAssert;",
            "import org.springframework.beans.factory.annotation.Autowired;",
            "import org.springframework.beans.factory.annotation.Value;",
            "import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;",
            "import org.springframework.test.context.bean.override.mockito.MockitoBean;",
            "import org.springframework.context.annotation.Import;",
            "import org.springframework.http.MediaType;",
            "import org.springframework.test.web.servlet.MockMvc;",
        ],
        "RepositoryTest.j2": [
            # Package wildcards
            f"import {model_class.package.entity}.*;" if model_class else None,
            f"import {util.Store.package.repository}.*;" if model_class else None,
            f"import {util.Store.package.model}.*;" if model_class else None,
            # Parent entity and repository imports
            *(
                [f"import {parent.model.package.entity}.{parent.model.name}Entity;" for parent in model_class.parents]
                if model_class
                else []
            ),
            *(
                [
                    f"import {parent.model.package.repository}.{parent.model.name}Repository;"
                    for parent in model_class.parents
                ]
                if model_class
                else []
            ),
            # Relation entity imports
            *(
                [
                    f"import {util.get_model_for(field.type).package.entity}.{util.get_model_for(field.type).name}Entity;"
                    for field in model_class.fields
                    if field.is_relation
                ]
                if model_class
                else []
            ),
            f"import {util.Store.package.util}.JsonUtil;",
            f"import {util.Store.config.base_package}.AbstractDataJpaTest;",
            f"import {util.Store.config.base_package}.TestUtils;",
            "import com.querydsl.core.BooleanBuilder;",
            "import com.querydsl.core.types.dsl.BooleanExpression;",
            "import java.util.List;",
            "import org.json.JSONObject;",
            "import org.junit.jupiter.api.Test;",
            "import org.skyscreamer.jsonassert.JSONAssert;",
            "import org.springframework.beans.factory.annotation.Autowired;",
            "import org.springframework.boot.jpa.test.autoconfigure.TestEntityManager;",
            "import static org.junit.jupiter.api.Assertions.assertEquals;",
        ],
        "ServiceTest.j2": [
            # *(model_class.imports["service_tests"] if model_class else []),
            f"import {util.Store.config.base_package}.TestConfig;",
            f"import {util.Store.config.base_package}.TestUtils;",
            f"import {util.Store.package.enum}.ErrorCode;",
            f"import {util.Store.package.exception}.AppException;",
            f"import {util.Store.package.model}.AppError;",
            f"import {util.Store.package.model}.CursorPage;",
            f"import {util.Store.package.model}.CursorPageable;",
            f"import {util.Store.package.util}.JsonUtil;",
            f"import {model_class.package.domain}.{model_class.name}Request;" if model_class else None,
            f"import {model_class.package.domain}.{model_class.name};" if model_class else None,
            f"import {model_class.package.entity}.{model_class.name}Entity;" if model_class else None,
            f"import {model_class.package.mapper}.{model_class.name}Mapper;" if model_class else None,
            f"import {model_class.package.repository}.{model_class.name}Repository;" if model_class else None,
            *(
                [
                    *[
                        f"import {parent.model.package.entity}.{parent.model.name}Entity;"
                        for parent in model_class.parents
                    ],
                    *[
                        f"import {parent.model.package.repository}.{parent.model.name}Repository;"
                        for parent in model_class.parents
                    ],
                ]
                if model_class
                else []
            ),
            "import static org.junit.jupiter.api.Assertions.assertEquals;",
            "import static org.junit.jupiter.api.Assertions.assertThrows;",
            "import static org.mockito.ArgumentMatchers.any;",
            "import static org.mockito.ArgumentMatchers.eq;",
            "import static org.mockito.Mockito.when;",
            "import com.querydsl.core.types.Predicate;",
            "import java.util.List;",
            "import java.util.Optional;",
            "import org.json.JSONArray;",
            "import org.json.JSONObject;",
            "import org.junit.jupiter.api.BeforeEach;",
            "import org.junit.jupiter.api.extension.ExtendWith;",
            "import org.junit.jupiter.api.Test;",
            "import org.skyscreamer.jsonassert.JSONAssert;",
            "import org.springframework.beans.factory.annotation.Autowired;",
            "import org.springframework.context.annotation.Import;",
            "import org.springframework.test.context.bean.override.mockito.MockitoBean;",
            "import org.springframework.test.context.junit.jupiter.SpringExtension;",
        ],
        "BaseController.j2": [
            f"import {util.Store.package.model}.Context;",
            "import jakarta.servlet.http.HttpServletRequest;",
            "import org.springframework.beans.factory.annotation.Autowired;",
        ],
        "AppConfiguration.j2": [
            f"import {util.Store.package.repository}.BaseRepositoryImpl;" if is_db else None,
            f"import {util.Store.package.util}.JsonMergePatchConverter;",
            f"import {util.Store.package.util}.JsonUtil;",
            "import com.fasterxml.jackson.dataformat.yaml.YAMLMapper;",
            "import java.util.List;",
            "import org.springframework.boot.jackson.autoconfigure.JsonMapperBuilderCustomizer;",
            "import org.springframework.context.annotation.Bean;",
            "import org.springframework.context.annotation.Configuration;",
            "import org.springframework.data.jpa.repository.config.EnableJpaRepositories;",
            "import org.springframework.http.converter.HttpMessageConverter;",
            "import org.springframework.stereotype.Component;",
            "import org.springframework.scheduling.annotation.EnableScheduling;",
            "import org.springframework.web.servlet.config.annotation.CorsRegistry;",
            "import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;",
            "import tools.jackson.databind.json.JsonMapper;",
        ],
        "ErrorCode.j2": [
            f"import {util.Store.package.model}.AppError;",
            "import org.springframework.http.HttpStatus;",
            "import java.util.List;",
            "import java.util.Objects;",
        ],
        "AppException.j2": [
            f"import {util.Store.package.enum}.ErrorCode;",
            f"import {util.Store.package.model}.AppError;",
            "import java.util.List;",
        ],
        "AppExceptionUtil.j2": [
            f"import {util.Store.package.enum}.ErrorCode;",
            "import org.springframework.util.function.ThrowingConsumer;",
            "import org.springframework.util.function.ThrowingSupplier;",
        ],
        "GlobalExceptionHandler.j2": [
            f"import {util.Store.package.enum}.ErrorCode;",
            f"import {util.Store.package.model}.AppError;",
            f"import {util.Store.package.model}.AppErrorBuilder;",
            "import lombok.extern.slf4j.Slf4j;",
            "import org.springframework.http.HttpHeaders;",
            "import org.springframework.http.HttpStatus;",
            "import org.springframework.http.HttpStatusCode;",
            "import org.springframework.http.ResponseEntity;",
            "import org.springframework.http.converter.HttpMessageNotReadableException;",
            "import org.springframework.validation.FieldError;",
            "import org.springframework.validation.ObjectError;",
            "import org.springframework.web.bind.MethodArgumentNotValidException;",
            "import org.springframework.web.bind.annotation.ControllerAdvice;",
            "import org.springframework.web.bind.annotation.ExceptionHandler;",
            "import org.springframework.web.context.request.ServletWebRequest;",
            "import org.springframework.web.context.request.WebRequest;",
            "import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;",
            "import tools.jackson.core.JacksonException;",
            "import tools.jackson.databind.exc.InvalidFormatException;",
            "import tools.jackson.databind.exc.MismatchedInputException;",
            "import jakarta.servlet.http.HttpServletRequest;",
            "import java.util.ArrayList;",
            "import java.util.List;",
        ],
        "AbstractPersistentBase.j2": [
            f"import {util.Store.package.util}.IdGenerator;",
            "import com.fasterxml.jackson.annotation.JsonIgnore;",
            "import jakarta.persistence.GeneratedValue;",
            "import jakarta.persistence.GenerationType;",
            "import jakarta.persistence.Id;",
            "import jakarta.persistence.MappedSuperclass;",
            "import jakarta.persistence.PrePersist;",
            "import jakarta.persistence.Version;",
        ],
        "AbstractPersistentObject.j2": [
            f"import {util.Store.package.util}.IdGenerator;",
            "import com.fasterxml.jackson.annotation.JsonIgnore;",
            "import com.fasterxml.jackson.annotation.JsonProperty;",
            "import lombok.extern.slf4j.Slf4j;",
            "import org.apache.commons.lang3.reflect.FieldUtils;",
            "import jakarta.persistence.Column;",
            "import jakarta.persistence.GeneratedValue;",
            "import jakarta.persistence.GenerationType;",
            "import jakarta.persistence.Id;",
            "import jakarta.persistence.ManyToMany;",
            "import jakarta.persistence.ManyToOne;",
            "import jakarta.persistence.MappedSuperclass;",
            "import jakarta.persistence.OneToMany;",
            "import jakarta.persistence.OneToOne;",
            "import jakarta.persistence.PrePersist;",
            "import jakarta.persistence.Version;",
            "import java.lang.reflect.Field;",
            "import java.lang.reflect.Method;",
            "import java.util.Set;",
        ],
        "AppError.j2": [
            f"import {util.Store.package.util}.Time;",
            "import com.fasterxml.jackson.annotation.JsonProperty;",
            "import io.soabase.recordbuilder.core.RecordBuilder;",
            "import java.time.OffsetDateTime;",
            "import java.util.ArrayList;",
            "import java.util.List;",
        ],
        "AbstractRepository.j2": [
            f"import {util.Store.package.model}.AbstractPersistentObject;",
            "import org.springframework.data.repository.NoRepositoryBean;",
            "import java.io.Serializable;",
            "import java.util.Optional;",
        ],
        "BaseRepository.j2": [
            f"import {util.Store.package.model}.AbstractPersistentObject;",
            f"import {util.Store.package.model}.CursorPage;",
            f"import {util.Store.package.model}.CursorPageable;",
            "import com.querydsl.core.types.Predicate;",
            "import com.querydsl.jpa.impl.JPAQuery;",
            "import org.springframework.data.jpa.repository.JpaRepository;",
            "import org.springframework.data.repository.NoRepositoryBean;",
            "import jakarta.persistence.EntityManager;",
            "import java.io.Serializable;",
            "import java.util.List;",
        ],
        "BaseRepositoryImpl.j2": [
            f"import {util.Store.package.model}.AbstractPersistentObject;",
            f"import {util.Store.package.model}.CursorPage;",
            f"import {util.Store.package.model}.CursorPageable;",
            "import com.querydsl.core.types.Predicate;",
            "import com.querydsl.core.types.dsl.PathBuilder;",
            "import com.querydsl.jpa.impl.JPAQuery;",
            "import com.querydsl.jpa.impl.JPAQueryFactory;",
            "import org.springframework.data.jpa.repository.support.JpaEntityInformation;",
            "import org.springframework.data.jpa.repository.support.SimpleJpaRepository;",
            "import org.springframework.data.querydsl.SimpleEntityPathResolver;",
            "import jakarta.persistence.EntityManager;",
            "import java.io.Serializable;",
            "import java.util.Base64;",
            "import java.util.List;",
        ],
        "Validator.j2": [
            f"import {util.Store.package.enum}.ErrorCode;",
            f"import {util.Store.package.exception}.AppException;",
            "import jakarta.validation.ConstraintViolation;",
            "import jakarta.validation.Validation;",
            "import java.util.ArrayList;",
            "import java.util.Arrays;",
            "import java.util.List;",
            "import java.util.Objects;",
            "import java.util.Set;",
            "import java.util.stream.Collectors;",
        ],
        "AbstractDataJpaTest.j2": [
            f"import {util.Store.package.repository}.BaseRepositoryImpl;",
            "import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;",
            "import org.springframework.context.annotation.Import;",
            "import org.springframework.data.jpa.repository.config.EnableJpaRepositories;",
        ],
    }

    imports = import_sets.get(template_name, [])

    # Filter out None values and separate static imports from regular imports
    all_imports = [imp for imp in imports if imp]
    static_imports = sorted(set([imp for imp in all_imports if imp.startswith("import static ")]))
    regular_imports = sorted(set([imp for imp in all_imports if not imp.startswith("import static ")]))

    # Combine with blank line separator if both groups exist
    if static_imports and regular_imports:
        return static_imports + [""] + regular_imports
    elif static_imports:
        return static_imports
    else:
        return regular_imports
