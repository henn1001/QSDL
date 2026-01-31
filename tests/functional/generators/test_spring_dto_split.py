"""
Test suite to verify DTO split behavior for base types with @readOnly/@writeOnly directives.

Key insight: Object types (declared with 'type') always generate Request/Response DTOs because
they auto-generate a @readOnly ID field. This makes testing the split behavior on base types
more important, as they only split when explicitly annotated with @readOnly/@writeOnly.

Focus areas:
1. Base types without @readOnly/@writeOnly (no split)
2. Base types with @readOnly fields (split)
3. Base types with @writeOnly fields (split)
4. Base types used in extend api {} operations
5. Nested base types (extending other bases)
"""

import shutil
import textwrap
from pathlib import Path

from qsdl.core import generate


def wrapper_generate(test_input: str) -> Path:
    """Generates Spring Boot code and returns the output path."""
    test_input = textwrap.dedent(test_input)
    test_output = Path("srcgen/")

    # generate
    shutil.rmtree(test_output / "src", ignore_errors=True)
    assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

    return test_output


def file_exists(output_path: Path, relative_path: str) -> bool:
    """Check if a file exists."""
    return (output_path / relative_path).exists()


class TestBaseDtoSplitBehavior:
    """Test DTO split behavior for base types based on @readOnly/@writeOnly directives."""

    def test_base_without_readonly_writeonly_no_split(self) -> None:
        """
        Base type without @readOnly/@writeOnly should NOT generate Request DTO.
        API generator should use the base type directly, not append "Request" suffix.
        """
        schema = """
        title: "Test API"
        version: "1.0"
        
        base SimpleBase {
            name: String!
            description: String
            count: Int
        }
        
        extend api {
            createEntity(data: SimpleBase): SimpleBase @path("entity") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Base type without @readOnly/@writeOnly should NOT generate Request DTO
        assert file_exists(output, "src/main/java/app/server/domain/SimpleBase.java")
        assert not file_exists(output, "src/main/java/app/server/domain/SimpleBaseRequest.java")

        # API should reference SimpleBase directly (not SimpleBaseRequest)
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "ResponseEntity<SimpleBase> createEntity" in api_content
        assert "SimpleBase data" in api_content

    def test_base_with_readonly_splits(self) -> None:
        """Base type with @readOnly fields should generate both Request and Response DTOs."""
        schema = """
        title: "Test API"
        version: "1.0"
        
        base AuditedBase {
            name: String!
            description: String
            created_at: Date @readOnly
            created_by: String @readOnly
        }
        
        extend api {
            createAudited(data: AuditedBase): AuditedBase @path("audited") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Should generate both Request and Response DTOs
        assert file_exists(output, "src/main/java/app/server/domain/AuditedBase.java")
        assert file_exists(output, "src/main/java/app/server/domain/AuditedBaseRequest.java")

        # Verify Request DTO does not contain @readOnly fields
        request_content = (output / "src/main/java/app/server/domain/AuditedBaseRequest.java").read_text()
        assert "createdAt" not in request_content
        assert "createdBy" not in request_content
        assert "name" in request_content
        assert "description" in request_content

        # Verify Response DTO contains @readOnly fields
        response_content = (output / "src/main/java/app/server/domain/AuditedBase.java").read_text()
        assert "createdAt" in response_content
        assert "createdBy" in response_content
        assert "name" in response_content

        # Verify API operation uses AuditedBaseRequest for input, AuditedBase for output
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "ResponseEntity<AuditedBase> createAudited" in api_content
        assert "AuditedBaseRequest data" in api_content

    def test_base_with_writeonly_splits(self) -> None:
        """Base type with @writeOnly fields should generate both Request and Response DTOs."""
        schema = """
        title: "Test API"
        version: "1.0"
        
        base SecureBase {
            username: String!
            password: String @writeOnly
            email: String
        }
        
        extend api {
            register(credentials: SecureBase): SecureBase @path("register") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Should generate both Request and Response DTOs
        assert file_exists(output, "src/main/java/app/server/domain/SecureBase.java")
        assert file_exists(output, "src/main/java/app/server/domain/SecureBaseRequest.java")

        # Verify Request DTO contains @writeOnly field
        request_content = (output / "src/main/java/app/server/domain/SecureBaseRequest.java").read_text()
        assert "password" in request_content
        assert "username" in request_content

        # Verify Response DTO does not contain @writeOnly field
        response_content = (output / "src/main/java/app/server/domain/SecureBase.java").read_text()
        assert "password" not in response_content
        assert "username" in response_content

        # Verify API operation uses SecureBaseRequest for input, SecureBase for output
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "ResponseEntity<SecureBase> register" in api_content
        assert "SecureBaseRequest credentials" in api_content

    def test_base_with_both_readonly_and_writeonly(self) -> None:
        """Base type with both @readOnly and @writeOnly should generate both DTOs with correct fields."""
        schema = """
        title: "Test API"
        version: "1.0"
        
        base ComplexBase {
            name: String!
            password: String @writeOnly
            created_at: Date @readOnly
            updated_at: Date @readOnly
        }
        
        extend api {
            createComplex(data: ComplexBase): ComplexBase @path("complex") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Should generate both Request and Response DTOs
        assert file_exists(output, "src/main/java/app/server/domain/ComplexBase.java")
        assert file_exists(output, "src/main/java/app/server/domain/ComplexBaseRequest.java")

        # Verify Request DTO has @writeOnly but not @readOnly fields
        request_content = (output / "src/main/java/app/server/domain/ComplexBaseRequest.java").read_text()
        assert "password" in request_content
        assert "name" in request_content
        assert "createdAt" not in request_content
        assert "updatedAt" not in request_content

        # Verify Response DTO has @readOnly but not @writeOnly fields
        response_content = (output / "src/main/java/app/server/domain/ComplexBase.java").read_text()
        assert "password" not in response_content
        assert "name" in response_content
        assert "createdAt" in response_content
        assert "updatedAt" in response_content

    def test_nested_base_extends_base_with_readonly(self) -> None:
        """Base extending another base with @readOnly should inherit split behavior."""
        schema = """
        title: "Test API"
        version: "1.0"
        
        base BaseEntity {
            name: String!
            created_at: Date @readOnly
        }
        
        base ExtendedEntity extends BaseEntity {
            description: String
            version: Int
        }
        
        extend api {
            createExtended(data: ExtendedEntity): ExtendedEntity @path("extended") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Only ExtendedEntity generates DTOs (it's used in API)
        # BaseEntity is only extended, not used directly in API, so no standalone DTO generated
        assert not file_exists(output, "src/main/java/app/server/domain/BaseEntity.java")
        assert not file_exists(output, "src/main/java/app/server/domain/BaseEntityRequest.java")
        assert file_exists(output, "src/main/java/app/server/domain/ExtendedEntity.java")
        assert file_exists(output, "src/main/java/app/server/domain/ExtendedEntityRequest.java")

        # Verify ExtendedEntityRequest does not contain inherited @readOnly field
        request_content = (output / "src/main/java/app/server/domain/ExtendedEntityRequest.java").read_text()
        assert "createdAt" not in request_content
        assert "name" in request_content
        assert "description" in request_content

        # Verify ExtendedEntity contains inherited @readOnly field
        response_content = (output / "src/main/java/app/server/domain/ExtendedEntity.java").read_text()
        assert "createdAt" in response_content
        assert "name" in response_content

    def test_nested_base_extends_base_without_readonly(self) -> None:
        """
        Base extending another base without @readOnly should not split.
        API generator should use the base type directly, not append "Request" suffix.
        """
        schema = """
        title: "Test API"
        version: "1.0"
        
        base PlainBase {
            name: String!
            value: Int
        }
        
        base EnhancedBase extends PlainBase {
            description: String
            active: Boolean
        }
        
        extend api {
            process(input: EnhancedBase): EnhancedBase @path("process") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Only EnhancedBase generates DTO (it's used in API)
        # PlainBase is only extended, not used directly, so no DTO generated
        assert not file_exists(output, "src/main/java/app/server/domain/PlainBase.java")
        assert not file_exists(output, "src/main/java/app/server/domain/PlainBaseRequest.java")
        assert file_exists(output, "src/main/java/app/server/domain/EnhancedBase.java")
        assert not file_exists(output, "src/main/java/app/server/domain/EnhancedBaseRequest.java")

        # API should reference EnhancedBase directly (not EnhancedBaseRequest)
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "ResponseEntity<EnhancedBase> process" in api_content
        assert "EnhancedBase input" in api_content

    def test_base_with_nested_base_field(self) -> None:
        """
        Base type containing another base as field should handle split correctly.

        When a base type is used as a field in another base type, both generate DTOs
        and the nested type also splits if it has @readOnly/@writeOnly fields.
        """
        schema = """
        title: "Test API"
        version: "1.0"
        
        base Address {
            street: String!
            city: String!
            created_at: Date @readOnly
        }
        
        base Person {
            name: String!
            address: Address
            age: Int
        }
        
        extend api {
            createPerson(person: Person): Person @path("person") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Both Person and Address generate Request/Response DTOs
        # Address splits because it has @readOnly field
        # Person must also split (transitively) because it contains Address
        assert file_exists(output, "src/main/java/app/server/domain/Address.java")
        assert file_exists(output, "src/main/java/app/server/domain/AddressRequest.java")
        assert file_exists(output, "src/main/java/app/server/domain/Person.java")
        assert file_exists(output, "src/main/java/app/server/domain/PersonRequest.java")

        # Verify Address Response contains @readOnly field
        address_response_content = (output / "src/main/java/app/server/domain/Address.java").read_text()
        assert "createdAt" in address_response_content

        # Verify AddressRequest excludes @readOnly field
        address_request_content = (output / "src/main/java/app/server/domain/AddressRequest.java").read_text()
        assert "createdAt" not in address_request_content
        assert "street" in address_request_content
        assert "city" in address_request_content

        # Verify PersonRequest references AddressRequest (not Address)
        person_request_content = (output / "src/main/java/app/server/domain/PersonRequest.java").read_text()
        assert "AddressRequest address" in person_request_content
        assert "name" in person_request_content
        assert "age" in person_request_content

        # Verify Person Response references full Address type
        person_content = (output / "src/main/java/app/server/domain/Person.java").read_text()
        assert "Address address" in person_content

        # Verify API uses PersonRequest for input and Person for output
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "ResponseEntity<Person> createPerson" in api_content
        assert "PersonRequest person" in api_content

    def test_base_with_nested_base_field_response_only(self) -> None:
        """
        Base type containing another base with @readOnly/@writeOnly used only in response.

        When Person is only used as a response (not request), PersonRequest should NOT
        be generated even though Address forces split. Only Person (response) and
        AddressRequest/Address should be generated.
        """
        schema = """
        title: "Test API"
        version: "1.0"
        
        base Address {
            street: String!
            city: String!
            created_at: Date @writeOnly
        }
        
        base Person {
            name: String!
            address: Address
            age: Int
        }
        
        extend api {
            getPerson(): Person @path("person") @method(GET)
        }
        """

        output = wrapper_generate(schema)

        # Address splits because it has @readOnly field
        # Only used in response, so no Request DTO
        assert file_exists(output, "src/main/java/app/server/domain/Address.java")
        assert not file_exists(output, "src/main/java/app/server/domain/AddressRequest.java")

        # Person should only generate response DTO (not PersonRequest)
        # because it's only used as a response type and doesn't have its own @readOnly/@writeOnly
        assert file_exists(output, "src/main/java/app/server/domain/Person.java")
        assert not file_exists(output, "src/main/java/app/server/domain/PersonRequest.java")

        # Verify Address Response contains @readOnly field
        address_response_content = (output / "src/main/java/app/server/domain/Address.java").read_text()
        assert "createdAt" not in address_response_content

        # Verify Person Response references full Address type
        person_content = (output / "src/main/java/app/server/domain/Person.java").read_text()
        assert "Address address" in person_content
        assert "name" in person_content
        assert "age" in person_content

        # Verify API uses only Person for output (no PersonRequest needed)
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "ResponseEntity<Person> getPerson" in api_content
        assert "PersonRequest" not in api_content

    def test_base_with_nested_base_field_request_only(self) -> None:
        """
        Base type containing another base with @readOnly/@writeOnly used only in request.

        When Person is only used as a request (not response), PersonRequest should be generated
        even though Address forces split. Only PersonRequest and AddressRequest/Address should
        be generated.
        """
        schema = """
        title: "Test API"
        version: "1.0"
        
        base Address {
            street: String!
            city: String!
            created_at: Date @readOnly
        }
        
        base Person {
            name: String!
            address: Address
            age: Int
        }
        
        extend api {
            createPerson(person: Person): Void @path("person") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Address splits because it has @readOnly field
        # Only used in request, so no Response DTO
        assert not file_exists(output, "src/main/java/app/server/domain/Address.java")
        assert file_exists(output, "src/main/java/app/server/domain/AddressRequest.java")

        # Person should only generate request DTO (not Person)
        # because it's only used as a request type and doesn't have its own @readOnly/@writeOnly
        assert not file_exists(output, "src/main/java/app/server/domain/Person.java")
        assert file_exists(output, "src/main/java/app/server/domain/PersonRequest.java")

        # Verify AddressRequest excludes @readOnly field
        address_request_content = (output / "src/main/java/app/server/domain/AddressRequest.java").read_text()
        assert "createdAt" not in address_request_content
        assert "street" in address_request_content
        assert "city" in address_request_content

        # Verify PersonRequest references AddressRequest (not Address)
        person_request_content = (output / "src/main/java/app/server/domain/PersonRequest.java").read_text()
        assert "AddressRequest address" in person_request_content
        assert "name" in person_request_content
        assert "age" in person_request_content

        # Verify API uses PersonRequest for input and no Person response
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "createPerson" in api_content
        assert "PersonRequest person" in api_content
        assert "ResponseEntity<Person>" not in api_content

    def test_multiple_api_operations_with_same_base(self) -> None:
        """Multiple API operations using the same base should reuse DTOs correctly."""
        schema = """
        title: "Test API"
        version: "1.0"
        
        base UserData {
            username: String!
            email: String
            password: String @writeOnly
            last_login: Date @readOnly
        }
        
        extend api {
            register(user: UserData): UserData @path("register") @method(POST)
            updateProfile(user: UserData): UserData @path("profile") @method(PUT)
            getProfile(): UserData @path("profile") @method(GET)
        }
        """

        output = wrapper_generate(schema)

        # Should generate both Request and Response DTOs (only once)
        assert file_exists(output, "src/main/java/app/server/domain/UserData.java")
        assert file_exists(output, "src/main/java/app/server/domain/UserDataRequest.java")

        # Verify all API operations use the correct DTO variants
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "ResponseEntity<UserData> register" in api_content
        assert "UserDataRequest user" in api_content
        assert "ResponseEntity<UserData> updateProfile" in api_content
        assert "ResponseEntity<UserData> getProfile" in api_content

    def test_base_with_nested_object_field(self) -> None:
        """
        Base type containing an Object (not Base) as field should handle split correctly.

        Object types always split (because they auto-generate an ID field with @readOnly).
        When a base contains an object field, the base must also split transitively.
        """
        schema = """
        title: "Test API"
        version: "1.0"
        
        type Company {
            name: String!
            city: String!
        }
        
        base Employee {
            firstName: String!
            lastName: String!
            company: Company
            salary: Int
        }
        
        extend api {
            createEmployee(employee: Employee): Employee @path("employee") @method(POST)
        }
        """

        output = wrapper_generate(schema)

        # Company is an Object, so it always generates Request/Response (due to auto-generated ID)
        assert file_exists(output, "src/main/java/app/server/domain/entity/CompanyEntity.java")
        assert file_exists(output, "src/main/java/app/server/domain/Company.java")
        assert file_exists(output, "src/main/java/app/server/domain/CompanyRequest.java")

        # Employee must also split (transitively) because it contains Company
        assert file_exists(output, "src/main/java/app/server/domain/Employee.java")
        assert file_exists(output, "src/main/java/app/server/domain/EmployeeRequest.java")

        # Verify EmployeeRequest references CompanyRequest
        employee_request_content = (output / "src/main/java/app/server/domain/EmployeeRequest.java").read_text()
        assert "CompanyRequest company" in employee_request_content
        assert "firstName" in employee_request_content
        assert "lastName" in employee_request_content

        # Verify Employee Response references full Company type
        employee_content = (output / "src/main/java/app/server/domain/Employee.java").read_text()
        assert "Company company" in employee_content

        # Verify API uses EmployeeRequest for input and Employee for output
        api_content = (output / "src/main/java/app/server/api/DefaultApi.java").read_text()
        assert "ResponseEntity<Employee> createEmployee" in api_content
        assert "EmployeeRequest employee" in api_content
