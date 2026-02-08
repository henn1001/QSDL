# PlantUML generator

The PlantUML generator produces a markdown file with embedded PlantUML diagrams that visualize your schema structure. It generates three diagrams: one for enums, one for base types, and one for domain objects with their relationships and operations.

## Output

The generator creates a `plantuml.md` file containing PlantUML class diagrams and automatically converts them to PNG images (`.enums.png`, `.bases.png`, `.overview.png`) for easy viewing.

## Diagrams

- **Enums**: All enumeration types defined in the schema.
- **Bases**: All base types and their inheritance relationships.
- **Overview**: Domain objects with their fields, operations, and composition/aggregation relationships (shown as `--*` and `--o` connectors).
