from qsdl.generators.spring.config import Database

from . import models as spring
from . import util


def render_imports(template_name: str, api_or_model: spring.ApiClass | spring.ModelClass | None) -> list[str]:
    api_class: spring.ApiClass | None = None
    model_class: spring.ModelClass | None = None

    if api_or_model and isinstance(api_or_model, spring.ApiClass):
        api_class = api_or_model
    if api_or_model and isinstance(api_or_model, spring.ModelClass):
        model_class = api_or_model

    import_sets = {
        "Api.j2": [
            *([f"import {api_class.package.domain}.*;"] if api_class else []),
            f"import {util.Store.package.enum}.*;",
            f"import {util.Store.package.model}.CursorPage;",
            f"import {util.Store.package.model}.CursorPageable;",
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
            "import com.fasterxml.jackson.databind.node.ObjectNode;",
            "import java.util.List;",
        ],
        "Controller.j2": [
            *([f"import {api_class.package.api}.{api_class.name}Api;"] if api_class else []),
            *([f"import {api_class.package.domain}.*;"] if api_class else []),
            *(
                [f"import {api_class.package.service}.{api_class.name}Service;"]
                if api_class and api_class.has_generated
                else []
            ),
            f"import {util.Store.package.controller}.BaseController;",
            f"import {util.Store.package.util}.Validator;",
            f"import {util.Store.package.enum}.*;",
            f"import {util.Store.package.model}.CursorPage;",
            f"import {util.Store.package.model}.CursorPageable;",
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
            "import com.fasterxml.jackson.databind.node.ObjectNode;",
            "import java.util.List;",
            "import lombok.AllArgsConstructor;",
        ],
        "Service.j2": [
            *([f"import {api_class.package.domain}.*;"] if api_class else []),
            *(
                [
                    f"import {api_class.package.entity}.*;",
                    f"import {api_class.package.mapper}.*;",
                    f"import {api_class.package.repository}.*;",
                    f"import {util.Store.package.repository}.*;",
                    f"import {util.Store.package.util}.PredicateBuilder;",
                ]
                if api_class and util.Store.config.database == Database.HIBERNATE
                else []
            ),
            *(
                [
                    *[f"import {parent.model.package.domain}.*;" for parent in api_class.model.parents],
                    *[f"import {parent.model.package.entity}.*;" for parent in api_class.model.parents],
                    *[f"import {parent.model.package.mapper}.*;" for parent in api_class.model.parents],
                    *[f"import {parent.model.package.repository}.*;" for parent in api_class.model.parents],
                ]
                if api_class and util.Store.config.database == Database.HIBERNATE and api_class.model
                else []
            ),
            f"import {util.Store.package.enum}.*;",
            f"import {util.Store.package.model}.Context;",
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
        "BaseController.j2": [
            f"import {util.Store.package.model}.Context;",
            "import jakarta.servlet.http.HttpServletRequest;",
            "import org.springframework.beans.factory.annotation.Autowired;",
        ],
        "AppConfiguration.j2": [
            f"import {util.Store.package.util}.Json;",
            f"import {util.Store.package.repository}.BaseRepositoryImpl;",
            "import com.fasterxml.jackson.databind.ObjectMapper;",
            "import com.fasterxml.jackson.dataformat.yaml.YAMLMapper;",
            "import java.util.TimeZone;",
            "import org.springframework.beans.factory.annotation.Value;",
            "import org.springframework.boot.context.event.ApplicationReadyEvent;",
            "import org.springframework.context.annotation.Bean;",
            "import org.springframework.context.annotation.Configuration;",
            "import org.springframework.context.event.EventListener;",
            "import org.springframework.data.jpa.repository.config.EnableJpaRepositories;",
            "import org.springframework.scheduling.annotation.EnableScheduling;",
            "import org.springframework.web.servlet.config.annotation.CorsRegistry;",
            "import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;",
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
            "import lombok.extern.slf4j.Slf4j;",
            "import org.springframework.http.HttpHeaders;",
            "import org.springframework.http.HttpStatus;",
            "import org.springframework.http.HttpStatusCode;",
            "import org.springframework.http.ResponseEntity;",
            "import org.springframework.validation.DataBinder;",
            "import org.springframework.validation.FieldError;",
            "import org.springframework.validation.ObjectError;",
            "import org.springframework.web.bind.MethodArgumentNotValidException;",
            "import org.springframework.web.bind.annotation.ControllerAdvice;",
            "import org.springframework.web.bind.annotation.ExceptionHandler;",
            "import org.springframework.web.bind.annotation.InitBinder;",
            "import org.springframework.web.context.request.ServletWebRequest;",
            "import org.springframework.web.context.request.WebRequest;",
            "import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;",
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
            "import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;",
            "import org.springframework.context.annotation.Import;",
            "import org.springframework.data.jpa.repository.config.EnableJpaRepositories;",
        ],
    }

    imports = import_sets.get(template_name, [])
    return sorted(set(imports))
