# Guidelines For Contributing

## Tools

* python 3.6+
* make
* vscode

## Styleguides and Coding conventions

Code change should conform to the google [styleguide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md).

| Types                      | Convention         | Internal                         |
| -------------------------- | ------------------ | -------------------------------- |
| Packages                   | lower_with_under   |                                  |
| Modules                    | lower_with_under   | lower_with_under                 |
| Classes                    | CapWords           | \_CapWords                       |
| Exceptions                 | CapWords           |                                  |
| Functions                  | lower_with_under() | \_lower_with_under()             |
| Global/Class Constants     | CAPS_WITH_UNDER    | \_CAPS_WITH_UNDER                |
| Global/Class Variables     | lower_with_under   | \_lower_with_under               |
| Instance Variables         | lower_with_under   | \_lower_with_under (protected)   |
| Method Names               | lower_with_under() | \_lower_with_under() (protected) |
| Function/Method Parameters | lower_with_under   |                                  |
| Local Variables            | lower_with_under   |                                  |

As a formatter we use [black](https://github.com/psf/black) with `--line-length 100`.

For inline comments use block types:

```python
# some
# comment 
# here
```

For function and class descriptions use multiline comments.

```python
class SampleClass(object):
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    def __init__(self, likes_spam=False):
        """Inits SampleClass with blah."""
        self.likes_spam = likes_spam
        self.eggs = 0

    def public_method(self):
        """Performs operation blah."""
```

## General conventions

### Versioning

Follow (Semantic Versioning)[https://semver.org/].

### Commit messages

Follow (Conventional Commits)[https://www.conventionalcommits.org/en/v1.0.0/].

## Getting Started

Install [poetry](https://python-poetry.org/docs/):

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

Create the python environment:

```bash
make setup
```

Create a copy of the vscode config files:

```bash
cp .vscode/launch.json.template .vscode/launch.json
cp .vscode/settings.json.template .vscode/settings.json
```
