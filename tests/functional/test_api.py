from tests import wrapper_generate


class TestApi:
    """Test Operations.

    01. `Api` can at least contain one `Operation`.

    02. `Api` may be used multiple times for a schema to define custom operations.

    03. `Api` may be used once inside a `Object` to overwrite the default CRUD operations.

    04. Routes are globally unique by HTTP method and normalized path. This overlaps with all used routes including `Object`s.

    05. Operation IDs must be globally unique. This overlaps with auto generated CRUD operations for `Object`s.

    """

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
        assert "patch" not in openapi["paths"]["/foos"]
        assert "delete" not in openapi["paths"]["/foos"]
