# i18n generator

The i18n generator produces YAML translation files from your schema, making it easy to generate a foundation for frontend translations and localization resources.

## Output

The generator creates locale-specific translation files (YAML by default) containing:

- **Objects and Bases**: Nested field hierarchies with human-readable labels (sentence case by default for the primary locale).
- **Enums**: All enumeration values mapped to readable capitalized labels.
- **Multiple locales**: Primary locale (`locale`) with auto-generated labels, plus any `extra_locales` with placeholder structure.

Files are organized by locale folder (e.g., `en/`, `de/`, `fr/`).

## Configuration

| Name                    | Type    | Default      | Description                                                                                 | Required |
| ----------------------- | ------- | ------------ | ------------------------------------------------------------------------------------------- | -------- |
| `locale`                | string  | `"en"`       | Primary locale (labels auto-generated for this language).                                   | No       |
| `extra_locales`         | string  | `""`         | Comma-separated list of additional locales to generate (e.g., `"de, fr, es"`).              | No       |
| `subfolder`             | string  | `""`         | Optional subfolder under each locale directory (e.g., `"translations"`).                    | No       |
| `enum`                  | boolean | `true`       | Include enum types in output.                                                               | No       |
| `base`                  | boolean | `true`       | Include base types in output.                                                               | No       |
| `object`                | boolean | `true`       | Include object types in output.                                                             | No       |
| `split_files`           | boolean | `false`      | Generate one file per entity (type).                                                        | No       |
| `single_file`           | boolean | `true`       | Generate consolidated files for objects/bases and enums.                                    | No       |
| `single_file_name`      | string  | `"domain"`   | Filename prefix for object/base translations (when `single_file=true`).                     | No       |
| `single_file_enum_name` | string  | `"constant"` | Filename prefix for enum translations (when `single_file=true`).                            | No       |
| `flatten`               | boolean | `false`      | Flatten nested structure to dot notation (e.g., `User.profile.name` → `User.profile.name`). | No       |
| `file_extension`        | string  | `"yaml"`     | Output file extension (e.g., `"yaml"`, `"yml"`, `"json"`).                                  | No       |
| `remove_unused_keys`    | boolean | `false`      | When merging with existing files, remove keys no longer in schema.                          | No       |

## Output Modes

### Single file mode (default: `single_file=true`)

Generates one file per locale containing all objects and bases under a `domain.*` prefix and enums under a `constant.*` prefix:

```
en/domain.yaml
en/constant.yaml
de/domain.yaml
de/constant.yaml
```

### Split files mode (`split_files=true`)

Generates one file per entity type per locale:

```
en/User.yaml
en/Address.yaml
en/Status.yaml
de/User.yaml
de/Address.yaml
de/Status.yaml
```

### Multiple files mode (default when `single_file=false`, `split_files=false`)

Generates separate `domain.yaml` and `constant.yaml` files per locale:

```
en/domain.yaml
en/constant.yaml
de/domain.yaml
de/constant.yaml
```

## Example

Given a schema with an `User` object and `Status` enum:

**Primary locale (en)** — labels are auto-generated:

```yaml
domain.User:
  __: User
  id: Id
  email: Email
  fullName: Full name
constant.Status:
  ACTIVE: Active
  INACTIVE: Inactive
```

**Extra locale (de)** — structure is generated, awaiting translation:

```yaml
domain.User:
  __: null
  id: null
  email: null
  fullName: null
constant.Status:
  ACTIVE: null
  INACTIVE: null
```

When merged with existing files, the generator preserves your manual translations and adds placeholders for new fields.

## Use in Frontend

Export the generated YAML files to your frontend build pipeline:

- **Config-based approach**: Point your frontend i18n library (e.g., i18next, Vue i18n, Nuxt i18n) to the locale folders.
- **Build-time integration**: Include generated files in your build process to ensure translations stay in sync with schema changes.
