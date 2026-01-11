import shutil
import subprocess
import textwrap
from pathlib import Path

from qsdl.core import generate


def wrapper_generate(test_input: str) -> Path:
    """Generates Spring Boot code and returns the output path.

    Args:
        test_input (str): The QSDL definition.

    Returns:
        Path: The output directory path.
    """
    test_input = textwrap.dedent(test_input)
    test_output = Path("srcgen/")

    # generate
    shutil.rmtree(test_output / "src", ignore_errors=True)
    assert generate(test_output, generator_name="spring", raw_schema=test_input) is None

    return test_output


def read_java_file(output_path: Path, relative_path: str) -> str:
    """Reads a generated Java file.

    Args:
        output_path: The root output directory
        relative_path: Relative path to the Java file (e.g., 'src/main/java/app/server/domain/entity/UserEntity.java')

    Returns:
        The file content as string
    """
    file_path = output_path / relative_path
    assert file_path.exists(), f"Expected file not found: {file_path}"
    return file_path.read_text(encoding="utf-8")


def assert_contains(content: str, *patterns: str) -> None:
    """Asserts that content contains all specified patterns.

    Args:
        content: The content to search in
        patterns: Patterns that must be present in the content
    """
    for pattern in patterns:
        assert pattern in content, f"Expected pattern not found: {pattern}\n\nContent:\n{content}"


def assert_not_contains(content: str, *patterns: str) -> None:
    """Asserts that content does NOT contain any of the specified patterns.

    Args:
        content: The content to search in
        patterns: Patterns that must NOT be present in the content
    """
    for pattern in patterns:
        assert pattern not in content, f"Unexpected pattern found: {pattern}\n\nContent:\n{content}"


def assert_tests_succeed() -> None:
    assert subprocess.call(["/bin/bash", "-i", "-c", "mvn clean test"], cwd="srcgen/") == 0


class TestGeneratorSpring:
    """Test spring generator"""

    # ============================================================================
    # GROUP 1: BASE TYPE FIELD FLATTENING TESTS (Phase 3.3)
    # ============================================================================

    def test_default_flattening_entity(self) -> None:
        """Default (no directive): field: Base should flatten columns inline with prefixes"""
        # Given
        test_input = """\
          base Address {
            street: String
            city: String
            zipCode: String
          }

          type User {
            name: String!
            address: Address
          }
        """

        # When
        output_path = wrapper_generate(test_input)
        entity_content = read_java_file(output_path, "src/main/java/app/server/domain/entity/UserEntity.java")

        # Then: Verify flattened fields with @Column annotations
        assert_contains(
            entity_content,
            # Should have individual fields with prefixed column names
            '@Column(name = "address_street")',
            'private String addressStreet;',
            '@Column(name = "address_city")',
            'private String addressCity;',
            '@Column(name = "address_zip_code")',
            'private String addressZipCode;',
        )

        # Should NOT have @Embedded or @AttributeOverrides (fields are expanded inline)
        assert_not_contains(
            entity_content,
            "@Embedded",
            "@AttributeOverrides",
            "AddressEmbeddable",
            "@OneToOne",
            "@JoinColumn",
            "AddressEntity"
        )

    def test_opaque_jsonb_entity(self) -> None:
        """@opaque directive: field: Base @opaque should use @JdbcTypeCode for JSONB storage"""
        # Given
        test_input = """\
          base PerformanceData {
            nav: Float
            navCurrency: String
            totalExpenseRatio: Float
            benchmark: String
          }

          type FinancialInstrument {
            isin: String!
            performanceData: PerformanceData @opaque
          }
        """

        # When
        output_path = wrapper_generate(test_input)
        entity_content = read_java_file(output_path, "src/main/java/app/server/domain/entity/FinancialInstrumentEntity.java")

        # Then: Verify JSONB storage with @JdbcTypeCode
        assert_contains(
            entity_content,
            # Should have @JdbcTypeCode annotation for JSONB
            "@JdbcTypeCode(SqlTypes.JSON)",
            '@Column(name = "performance_data", columnDefinition = "jsonb")',
            "private PerformanceData performanceData;",
        )

        # Should NOT have flattened fields or entity relationships
        assert_not_contains(
            entity_content,
            "@Embedded",
            "@AttributeOverrides",
            "PerformanceDataEmbeddable",
            "@OneToOne",
            "@JoinColumn",
            "PerformanceDataEntity",
            "performanceDataNav",  # Should not have flattened fields
            "performanceDataNavCurrency",
        )

    def test_opaque_array_jsonb(self) -> None:
        """@opaque on arrays: field: [Base] @opaque should use @JdbcTypeCode for JSONB array"""
        # Given
        test_input = """\
          base Variant {
            size: String
            color: String
            price: Float
          }

          type Product {
            name: String!
            variants: [Variant] @opaque
          }
        """

        # When
        output_path = wrapper_generate(test_input)
        entity_content = read_java_file(output_path, "src/main/java/app/server/domain/entity/ProductEntity.java")

        # Then: Verify JSONB array storage
        assert_contains(
            entity_content,
            # Should have @JdbcTypeCode for JSONB array
            "@JdbcTypeCode(SqlTypes.JSON)",
            '@Column(name = "variants", columnDefinition = "jsonb")',
            "private List<Variant> variants;",
        )

        # Should NOT have join table or entity relationships
        assert_not_contains(
            entity_content,
            "@OneToMany",
            "@JoinColumn",
            "@ElementCollection",
            "VariantEntity",
            "Set<",  # Should be List, not Set (for arrays)
        )

    def test_mapper_with_flattened_fields(self) -> None:
        """Verify MapStruct mapper is generated for flattened base fields"""
        # Given
        test_input = """\
          base ContactInfo {
            email: String
            phone: String
          }

          type Customer {
            name: String!
            contact: ContactInfo
          }
        """

        # When
        output_path = wrapper_generate(test_input)

        # Verify Entity has flattened fields
        entity_content = read_java_file(output_path, "src/main/java/app/server/domain/entity/CustomerEntity.java")
        assert_contains(
            entity_content,
            "private String contactEmail;",
            "private String contactPhone;",
        )

        # Verify POJO (DTO) has nested structure
        pojo_content = read_java_file(output_path, "src/main/java/app/server/domain/Customer.java")
        assert_contains(
            pojo_content,
            "private ContactInfo contact;",
        )

        # Verify MapStruct mapper is generated with proper annotations
        mapper_content = read_java_file(output_path, "src/main/java/app/server/domain/mapper/CustomerMapStruct.java")
        assert_contains(
            mapper_content,
            "@Mapper",
            "CustomerEntity",
            "Customer",
        )

    # ============================================================================
    # GROUP 2: INTEGRATION TEST (Phase 3.3)
    # ============================================================================

    def test_full_compilation(self) -> None:
        """Integration test: Verify generated code compiles with Maven (all features)"""
        # Given - Complex schema with all base type features
        test_input = """\
          base Address {
            street: String
            city: String
            zipCode: String
          }

          base Metadata {
            tags: [String]
            properties: Object
            version: Int
          }

          base Variant {
            size: String
            color: String
            price: Float
          }

          type Company {
            name: String!
            headquarters: Address
            metadata: Metadata @opaque
            productVariants: [Variant] @opaque
          }
        """

        # When
        wrapper_generate(test_input)

        # Then - Verify all tests pass (compilation + unit tests)
        assert_tests_succeed()
