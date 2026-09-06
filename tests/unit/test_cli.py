import json
from pathlib import Path

from typer.testing import CliRunner

from qsdl.__main__ import app

runner = CliRunner()

CUSTOM_GENERATOR = """\
from dataclasses import dataclass
from pathlib import Path
from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import Schema
from qsdl.generators import Generator
from qsdl.generators.base_config import BaseConfig


@dataclass
class Config(BaseConfig):
    greeting: str = "hello"
    shout: bool = False


class CustomGenerator(Generator):
    config_class = Config

    def generate(self, schema: Schema, config: Config, output_path: Path | None) -> GeneratedFiles:
        files = GeneratedFiles()
        files.add_text("out.txt", config.greeting.upper() if config.shout else config.greeting)
        return files


generator = CustomGenerator()
"""

SCHEMA = "type User { name: String }\n"

OPTIONAL_GENERATOR = """\
from dataclasses import dataclass
from pathlib import Path
from qsdl.artifacts import GeneratedFiles
from qsdl.dsl import Schema
from qsdl.generators import Generator
from qsdl.generators.base_config import BaseConfig

@dataclass
class Config(BaseConfig):
    enabled: bool | None = None

class OptionalGenerator(Generator):
    config_class = Config

    def generate(self, schema: Schema, config: Config, output_path: Path | None) -> GeneratedFiles:
        files = GeneratedFiles()
        files.add_text("out.txt", str(config.enabled))
        return files

generator = OptionalGenerator()
"""


def _schema(tmp_path: Path) -> Path:
    schema = tmp_path / "s.qsdl"
    schema.write_text(SCHEMA, encoding="utf-8")
    return schema


class TestGenerate:
    def test_set_overrides_config_file(self, tmp_path: Path) -> None:
        schema = _schema(tmp_path)
        config_file = tmp_path / "base.json"
        config_file.write_text(json.dumps({"file_name": "V1.sql", "table_prefix": "T_"}), encoding="utf-8")
        output = tmp_path / "out"

        result = runner.invoke(
            app,
            [
                "generate",
                "postgres",
                "-i",
                str(schema),
                "-o",
                str(output),
                "-c",
                str(config_file),
                "-S",
                "table_prefix=app_",
            ],
        )

        assert result.exit_code == 0, result.output
        assert (output / "V1.sql").is_file()
        assert "app_user" in (output / "V1.sql").read_text(encoding="utf-8")

    def test_multiple_config_files_merge_in_order(self, tmp_path: Path) -> None:
        schema = _schema(tmp_path)
        first = tmp_path / "first.json"
        first.write_text(json.dumps({"file_name": "V1.sql", "table_prefix": "T_"}), encoding="utf-8")
        second = tmp_path / "second.json"
        second.write_text(json.dumps({"table_prefix": "app_"}), encoding="utf-8")
        output = tmp_path / "out"

        result = runner.invoke(
            app,
            ["generate", "postgres", "-i", str(schema), "-o", str(output), "-c", str(first), "-c", str(second)],
        )

        assert result.exit_code == 0, result.output
        assert (output / "V1.sql").is_file()
        assert "app_user" in (output / "V1.sql").read_text(encoding="utf-8")

    def test_unknown_key_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["generate", "postgres", "-i", str(_schema(tmp_path)), "-S", "bogus=1"])
        assert result.exit_code == 1

    def test_malformed_set_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["generate", "postgres", "-i", str(_schema(tmp_path)), "-S", "no-equals"])
        assert result.exit_code == 1

    def test_invalid_enum_value_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["generate", "openapi", "-i", str(_schema(tmp_path)), "-S", "id_type=BOGUS"])
        assert result.exit_code == 1

    def test_unknown_generator_fails(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["generate", "nosuch", "-i", str(_schema(tmp_path))])
        assert result.exit_code == 1

    def test_bool_and_enum_set_values(self, tmp_path: Path) -> None:
        schema = _schema(tmp_path)
        output = tmp_path / "out"
        result = runner.invoke(
            app,
            [
                "generate",
                "spring",
                "-i",
                str(schema),
                "-o",
                str(output),
                "-S",
                "use_auditing=true",
                "-S",
                "database=NO",
            ],
        )
        assert result.exit_code == 0, result.output

    def test_write_version_flag(self, tmp_path: Path) -> None:
        from qsdl import __version__

        output = tmp_path / "out"
        result = runner.invoke(
            app, ["generate", "void", "-i", str(_schema(tmp_path)), "-o", str(output), "--write-version"]
        )
        assert result.exit_code == 0, result.output
        assert (output / ".qversion").read_text(encoding="utf-8") == __version__


class TestConfig:
    def test_validate_rejects_bad_value(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["config", "validate", "spring", "-S", "database=BOGUS"])
        assert result.exit_code == 1

    def test_validate_constructs_config(self, tmp_path: Path) -> None:
        config_file = tmp_path / "c.json"
        config_file.write_text(json.dumps({"use_auditing": 123}), encoding="utf-8")
        result = runner.invoke(app, ["config", "validate", "spring", "-c", str(config_file)])
        assert result.exit_code == 1

    def test_validate_accepts_file_and_overrides(self, tmp_path: Path) -> None:
        config_file = tmp_path / "c.json"
        config_file.write_text(json.dumps({"database": "HIBERNATE"}), encoding="utf-8")
        result = runner.invoke(app, ["config", "validate", "spring", "-c", str(config_file), "-S", "title=X"])
        assert result.exit_code == 0, result.output

    def test_init_writes_defaults(self, tmp_path: Path) -> None:
        output = tmp_path / "spring.json"
        result = runner.invoke(app, ["config", "init", "spring", "-o", str(output)])
        assert result.exit_code == 0, result.output
        assert json.loads(output.read_text(encoding="utf-8"))["title"] == "SpringBootApp"

    def test_show_prints_json(self) -> None:
        result = runner.invoke(app, ["config", "show", "postgres"])
        assert result.exit_code == 0, result.output
        assert "V1_0_0__baseline.sql" in result.output


class TestCustomGenerators:
    def test_file_generator(self, tmp_path: Path) -> None:
        module = tmp_path / "my_gen.py"
        module.write_text(CUSTOM_GENERATOR, encoding="utf-8")
        output = tmp_path / "out"

        result = runner.invoke(
            app, ["generate", str(module), "-i", str(_schema(tmp_path)), "-o", str(output), "-S", "shout=true"]
        )

        assert result.exit_code == 0, result.output
        assert (output / "out.txt").read_text(encoding="utf-8") == "HELLO"

    def test_optional_bool_override(self, tmp_path: Path) -> None:
        module = tmp_path / "optional.py"
        module.write_text(OPTIONAL_GENERATOR, encoding="utf-8")
        output = tmp_path / "out"

        result = runner.invoke(
            app, ["generate", str(module), "-i", str(_schema(tmp_path)), "-o", str(output), "-S", "enabled=false"]
        )

        assert result.exit_code == 0, result.output
        assert (output / "out.txt").read_text(encoding="utf-8") == "False"

    def test_package_generator(self, tmp_path: Path) -> None:
        package = tmp_path / "my_pkg"
        package.mkdir()
        (package / "__init__.py").write_text(CUSTOM_GENERATOR, encoding="utf-8")
        output = tmp_path / "out"

        result = runner.invoke(app, ["generate", str(package), "-i", str(_schema(tmp_path)), "-o", str(output)])

        assert result.exit_code == 0, result.output
        assert (output / "out.txt").read_text(encoding="utf-8") == "hello"

    def test_shadow_rejected(self, tmp_path: Path) -> None:
        module = tmp_path / "spring.py"
        module.write_text(CUSTOM_GENERATOR, encoding="utf-8")
        result = runner.invoke(app, ["generate", str(module), "-i", str(_schema(tmp_path))])
        assert result.exit_code == 1

    def test_missing_contract_rejected(self, tmp_path: Path) -> None:
        module = tmp_path / "broken.py"
        module.write_text("X = 1\n", encoding="utf-8")
        result = runner.invoke(app, ["generate", str(module), "-i", str(_schema(tmp_path))])
        assert result.exit_code == 1
