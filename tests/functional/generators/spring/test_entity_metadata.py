from .spring_test_utils import SpringTestUtils


class TestSpringEntityMetadata:
    """Test Spring entity metadata handling."""

    def test_abstract_entity_date_aliases_are_reused(self) -> None:
        """Date metadata aliases should use the fields inherited from AbstractEntity."""
        test_input = """\
            base CamelAudit {
                creationDate: Datetime @readOnly
                modificationDate: Datetime @readOnly
            }

            base SnakeAudit {
                creation_date: Datetime @readOnly
                modification_date: Datetime @readOnly
            }

            type CamelObject extends CamelAudit {
                name: String!
            }

            type SnakeObject extends SnakeAudit {
                name: String!
            }
        """

        files = SpringTestUtils.generate(test_input, "util/domain_config.json")

        abstract_entity_content = SpringTestUtils.read_file(
            files, "src/main/java/app/server/common/model/AbstractEntity.java"
        )
        SpringTestUtils.assert_contains(
            abstract_entity_content,
            "OffsetDateTime getCreationDate()",
            "OffsetDateTime getModificationDate()",
        )

        aliases = {
            "CamelObject": ("creationDate", "modificationDate", "t_camel_object"),
            "SnakeObject": ("creation_date", "modification_date", "t_snake_object"),
        }
        postgres_content = SpringTestUtils.read_file(
            files, "src/main/resources/db/migration/V1_0_0__baseline.sql"
        )
        for model_name, (creation_alias, modification_alias, table_name) in aliases.items():
            entity_content = SpringTestUtils.read_file(
                files, f"src/main/java/app/server/common/db/{model_name}Entity.java"
            )
            SpringTestUtils.assert_not_contains(
                entity_content,
                "private OffsetDateTime creationDate;",
                "private OffsetDateTime modificationDate;",
            )

            dto_content = SpringTestUtils.read_file(
                files, f"src/main/java/app/server/common/dto/{model_name}.java"
            )
            SpringTestUtils.assert_contains(
                dto_content,
                f'@JsonProperty(value = "{creation_alias}")',
                f'@JsonProperty(value = "{modification_alias}")',
                "OffsetDateTime creationDate",
                "OffsetDateTime modificationDate",
            )

            mapper_content = SpringTestUtils.read_file(
                files, f"src/main/java/app/server/common/mapper/{model_name}Mapper.java"
            )
            SpringTestUtils.assert_contains(
                mapper_content,
                '@Mapping(target = "creationDate", ignore = true)',
                '@Mapping(target = "modificationDate", ignore = true)',
            )

            table_content = postgres_content.split(f"CREATE TABLE IF NOT EXISTS {table_name} (", 1)[1].split(");", 1)[0]
            assert table_content.count("creation_date TIMESTAMP") == 1
            assert table_content.count("modification_date TIMESTAMP") == 1
