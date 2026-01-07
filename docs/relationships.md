## 🔗 Relation Types in QSDL

QSDL supports different types of object relations to express ownership, cardinality, and API exposure. Relations can appear between `type` (domain objects) and `base` (reusable/nested structures).

All list relations are implemented using **join tables** in the database for consistency.

---

### 🧱 Default Relation Behavior

| Relation        | Target Kind | Cardinality | Default Ownership     | Database Mapping           |
| --------------- | ----------- | ----------- | --------------------- | -------------------------- |
| `role: Role`    | base        | 1:1         | Composition (default) | `@ManyToOne`               |
| `roles: [Role]` | base        | 1:N         | Composition (default) | `@ManyToMany + join table` |
| `admin: User`   | type        | 1:1         | Composition (default) | `@ManyToOne`               |
| `users: [User]` | type        | 1:N         | Composition (default) | `@ManyToMany + join table` |

> **Note:**  
> If neither `@composition` nor `@aggregation` is specified, **composition is the default**.  
> This means the parent entity (e.g., `Project`) fully owns the related objects.  
> When the parent is deleted, all owned children are also deleted (cascading delete).

---

### 🎯 Ownership Modifiers

Use `@composition` or `@aggregation` to define **ownership semantics**, which impact **API behavior**, not the underlying DB model.

#### `@composition` (explicit or default)

- Strong ownership (like a "part-of" relationship)
- Parent **creates, updates, and deletes** children
- API: fully embedded or nested under parent routes
- DB: `@OneToMany(cascade = ALL, orphanRemoval = true)`

#### `@aggregation`

- Weak ownership (referenced, not owned)
- Parent can list or link items, but does **not control lifecycle**
- API: references or partial includes
- DB: `@ManyToMany` or `@OneToMany`, no cascading

---

### 📘 Example

```qsdl
type Project {
    name: String!

    role: Role                // single embedded/nested value (composition by default)
    roles: [Role]             // list of value objects (composition by default)

    admin: User               // referenced domain object (composition by default)
    users: [User]             // referenced list (composition by default)

    tickets: [Ticket] @composition    // fully owned, part of the project
    milestones: [Milestone] @aggregation // loosely linked, managed elsewhere
}
```

In this example, unless `@aggregation` is specified, all relations are **composition** by default:  
Deleting a `Project` will also delete its `Role`, `User`, `roles`, `users`, and `tickets`.
