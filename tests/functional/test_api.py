from tests import wrapper_generate, wrapper_generate_failure


class TestApi:
    """Test Operations.

    01. `Api` can at least contain one `Operation`.

    02. `Api` may be used multiple times for a schema to define custom operations.

    03. `Api` may be used once inside a `Object` to overwrite the default CRUD operations.

    04. `Api` must only specify two methods per path (with and without ID). This overlaps with all used paths including `Object`s.

    05. `Api` names must be globally unique. This overlaps with auto generated CRUD operations for `Object`s.

    """

    def test_api_01_positive(self) -> None:
        """Verify empty Operation"""
        test_input = """\
            extend api {
            }
        """

        openapi = wrapper_generate(test_input)

        assert not openapi["paths"]

    def test_api_02_positive(self) -> None:
        """Verify Api multiple usage in schema"""
        test_input = """\
            extend api {
                getFoo: Object @path("foo")
            }

            extend api {
                getBar: Object @path("bar")
            }

            extend api {
                getFruit: Object @path("fruit")
            }
        """

        openapi = wrapper_generate(test_input)

        assert "get" in openapi["paths"]["/foo"]
        assert "getFoo" in openapi["paths"]["/foo"]["get"]["operationId"]

        assert "get" in openapi["paths"]["/bar"]
        assert "getBar" in openapi["paths"]["/bar"]["get"]["operationId"]

        assert "get" in openapi["paths"]["/fruit"]
        assert "getFruit" in openapi["paths"]["/fruit"]["get"]["operationId"]

    def test_api_03_positive(self) -> None:
        """Verify Api CRUD overwrite"""
        test_input = """\
            type Foo {
                name: String

                extend api {
                    getFoo: Foo @path("/foos")
                }
            }
        """

        openapi = wrapper_generate(test_input)

        assert "get" in openapi["paths"]["/foos"]
        assert "getFoo" in openapi["paths"]["/foos"]["get"]["operationId"]

        assert "post" not in openapi["paths"]["/foos"]
        assert "put" not in openapi["paths"]["/foos"]
        assert "patch" not in openapi["paths"]["/foos"]
        assert "delete" not in openapi["paths"]["/foos"]

    def test_api_03_negative(self) -> None:
        """Verify Api CRUD overwrite"""
        test_input = """\
            type Type {
                name: String

                extend api {
                    getType: Type
                }

                extend api {
                    getTypes: [Type]
                }
            }
        """

        wrapper_generate_failure(test_input)

    def test_api_04_negative(self) -> None:
        """Verify unique paths"""
        inputs = []

        test_input = """\
            extend api {
                getObject1: String @path("object")
                getObject2: String @path("object")
            }
        """
        inputs.append(test_input)

        test_input = """\
            type Type {
                name: String
            }

            extend api {
                getObject: String @path("types")
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)

    def test_api_05_negative(self) -> None:
        """Verify unique Api names"""
        inputs = []

        test_input = """\
            extend api {
                getObject: String @path("object1")
                getObject: String @path("object2")
            }
        """
        inputs.append(test_input)

        test_input = """\
            type Type {
                name: String
            }

            extend api {
                getType: String @path("test")
            }
        """
        inputs.append(test_input)

        for test_input in inputs:
            wrapper_generate_failure(test_input)
