import json
import subprocess
import sys
from pathlib import Path

import pytest
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

    @pytest.mark.parametrize(
        ("declaration", "directive", "validate_status"),
        [
            ("scalar Token @openapi(string)", "openapi", 0),
            ("type Token { field: String @readOnly() }", "readOnly", 1),
        ],
    )
    def test_rejects_invalid_schema_before_generator_or_writer(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, declaration: str, directive: str, validate_status: int
    ) -> None:
        from qsdl.generators import get_definition

        def unexpected_generate(schema: object, config: object, output_path: Path | None) -> None:
            pytest.fail("generation ran for an invalid schema")

        monkeypatch.setattr(get_definition("openapi").plugin, "generate", unexpected_generate)
        imported = tmp_path / "common.qsdl"
        imported.write_text(declaration, encoding="utf-8")
        root = tmp_path / "root.qsdl"
        root.write_text('import "common.qsdl"\ntype User { token: Token }\n', encoding="utf-8")
        output = tmp_path / "out"

        standalone = runner.invoke(app, ["validate", "-i", str(root)])
        assert standalone.exit_code == validate_status, standalone.output
        generated = runner.invoke(app, ["generate", "openapi", "-i", str(root), "-o", str(output), "--write-version"])
        assert generated.exit_code == 1, generated.output
        assert isinstance(generated.exception, SystemExit)
        assert f"{imported}:1:" in generated.stderr
        assert f"Invalid @{directive}" in generated.stderr
        assert not output.exists()

    def test_reports_syntax_error_without_traceback(self, tmp_path: Path) -> None:
        schema = tmp_path / "broken.qsdl"
        schema.write_text("type User { name String }\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "qsdl", "generate", "void", "-i", str(schema)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1, result.stderr
        assert f"{schema}:1:" in result.stderr
        assert "error [syntax]:" in result.stderr
        assert "Expected ':'" in result.stderr
        assert "Traceback" not in result.stderr

    def test_reports_same_core_diagnostics_as_validate(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from qsdl.generators import get_definition

        def unexpected_generate(*args: object) -> None:
            pytest.fail("generator invoked with an invalid schema")

        monkeypatch.setattr(get_definition("spring").plugin, "generate", unexpected_generate)
        (tmp_path / "a.qsdl").write_text('extend api { a: String @path("/a") @method(TRACE) }\n')
        root = tmp_path / "z.qsdl"
        root.write_text('import "a.qsdl"\nextend api { b: String @path("/b") @method(OPTIONS) }\n')
        output = tmp_path / "out"

        standalone = runner.invoke(app, ["validate", "-i", str(root)])
        generated = runner.invoke(app, ["generate", "spring", "-i", str(root), "-o", str(output), "--write-version"])
        assert standalone.exit_code == generated.exit_code == 1
        assert standalone.stderr == generated.stderr
        assert standalone.stderr.count("error [LOG-204]:") == 2
        assert not output.exists()

    def test_generator_directive_error_does_not_hide_core_collision(self, tmp_path: Path) -> None:
        root = tmp_path / "root.qsdl"
        root.write_text("""
            scalar Token @openapi(notQuoted)
            type User { token: Token }
            extend api { listUsers: String @path("/users") }
        """)

        standalone = runner.invoke(app, ["validate", "-i", str(root)])
        generated = runner.invoke(app, ["generate", "openapi", "-i", str(root)])
        assert standalone.exit_code == generated.exit_code == 1
        assert "Invalid @openapi" in generated.stderr
        assert "error [SEM-105]:" in standalone.stderr
        assert standalone.stderr in generated.stderr

    def test_write_version_flag(self, tmp_path: Path) -> None:
        from qsdl import __version__

        output = tmp_path / "out"
        result = runner.invoke(
            app, ["generate", "void", "-i", str(_schema(tmp_path)), "-o", str(output), "--write-version"]
        )
        assert result.exit_code == 0, result.output
        assert (output / ".qversion").read_text(encoding="utf-8") == __version__


class TestValidate:
    def test_accepts_relative_imports_without_loading_generators_or_writing(self, tmp_path: Path) -> None:
        imports = tmp_path / "lib"
        imports.mkdir()
        (imports / "common.qsdl").write_text("scalar Token @openapi(string)\n", encoding="utf-8")
        root = tmp_path / "schema.qsdl"
        root.write_text('import "lib/common.qsdl"\ntype Item { token: Token }\n', encoding="utf-8")
        before = set(tmp_path.rglob("*"))
        code = """
import runpy
import sys

sys.modules.update(dict.fromkeys(("qsdl.plugins", "qsdl.core", "qsdl.generators")))
runpy.run_module("qsdl.__main__", run_name="__main__")
"""
        result = subprocess.run(
            [sys.executable, "-c", code, "validate", "--input", "schema.qsdl"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout == ""
        assert "loading metamodel..." in result.stderr
        assert "loading schema..." in result.stderr
        assert "running schema validation..." in result.stderr
        assert "schema validation passed" in result.stderr
        assert set(tmp_path.rglob("*")) == before

    def test_reports_independent_errors_in_file_and_position_order(self, tmp_path: Path) -> None:
        imported = tmp_path / "a.qsdl"
        imported.write_text("type Imported { field: String @readOnly() }\n", encoding="utf-8")
        root = tmp_path / "z.qsdl"
        root.write_text(
            'import "a.qsdl"\ntype First { one: String one: String }\ntype Second { two: String two: String }\n',
            encoding="utf-8",
        )
        result = runner.invoke(app, ["validate", "-i", str(root)])
        assert result.exit_code == 1, result.output
        assert not result.stdout
        lines = result.stderr.splitlines()
        assert len(lines) == 3
        assert "\x1b[" not in result.stderr
        assert lines[0].startswith(f"{imported}:1:31: error [LOG-204]: Invalid @readOnly")
        assert lines[1].startswith(f"{root}:2:26: error [SEM-102]:")
        assert lines[2].startswith(f"{root}:3:27: error [SEM-102]:")
        assert set(tmp_path.iterdir()) == {root, imported}

    def test_colors_diagnostics_when_requested(self, tmp_path: Path) -> None:
        root = tmp_path / "root.qsdl"
        root.write_text('servers: ["ftp://example.test"]\n', encoding="utf-8")
        result = runner.invoke(app, ["validate", "-i", str(root)], env={"FORCE_COLOR": "1", "NO_COLOR": ""}, color=True)
        assert result.exit_code == 1, result.output
        assert "\x1b[36m" in result.stderr
        assert "\x1b[1;31merror\x1b[0m" in result.stderr
        assert "\x1b[33m[LOG-302]\x1b[0m" in result.stderr

    def test_omits_unknown_position(self, tmp_path: Path) -> None:
        root = tmp_path / "root.qsdl"
        root.write_text('servers: ["ftp://example.test"]\n', encoding="utf-8")
        result = runner.invoke(app, ["validate", "-i", str(root)])
        assert result.exit_code == 1, result.output
        assert result.stderr.startswith(f"{root}: error [LOG-302]:")


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
