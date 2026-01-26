from tests import wrapper_generate
from tests.functional import wrapper_generate_failure


class TestSpecificsQuery:
    """Test specific functionality."""

    def test_query_negative_scalar_base_mixture(self) -> None:
        test_input = """\
        base Bar {
          field: String
        }
        extend api {
          getType(one: String, two: Bar): String @path("test")
        }
        """
        wrapper_generate_failure(test_input)

    def test_query_negative_scalar_object_mixture(self) -> None:
        test_input = """\
        type Bar {
          field: String
        }
        extend api {
          getType(one: String, two: Bar): String @path("test")
        }
        """
        wrapper_generate_failure(test_input)

    def test_query_negative_double_base(self) -> None:
        test_input = """\
        base Fruit {
          field: String
        }
        base Bar {
          field: String
        }
        extend api {
          getType(fruit: Fruit, bar: Bar): String @path("test")
        }
        """
        wrapper_generate_failure(test_input)

    def test_query_negative_query_on_base(self) -> None:
        test_input = """\
        base Bar {
          field: String
        }
        type Foo {
          flower: Bar @query
        }
        """
        wrapper_generate_failure(test_input)

    def test_query_negative_query_on_object(self) -> None:
        test_input = """\
        type Bar {
          field: String
        }
        type Foo {
          flower: Bar @query
        }
        """
        wrapper_generate_failure(test_input)

    def test_query_negative_nesting_in_base_filters(self) -> None:
        test_input = """\
        base Foo {
          field: String
        }
        base Bar {
          field: String
          nested: Foo
        }
        extend api {
          getType(query: Bar): String @path("test")
        }
        """
        wrapper_generate_failure(test_input)

    def test_query_negative_nesting_in_base_filters_extends(self) -> None:
        test_input = """\
        base Fruit {
          field: String
        }
        base Foo {
          field: String
          nested: Fruit
        }
        base Bar extends Foo {
          fuld: String
        }
        extend api {
          getType(query: Bar): String @path("test")
        }
        """
        wrapper_generate_failure(test_input)

    def test_query_positive_no_filter_at_threshold(self) -> None:
        test_input = """\
        extend api {
          search(name: String, status: String, archived: Boolean): Void @path("search")
        }
        """

        openapi = wrapper_generate(test_input)

        parameters = openapi["paths"]["/search"]["get"]["parameters"]
        assert len(parameters) == 3
        assert parameters[0]["name"] == "name"
        assert parameters[1]["name"] == "status"
        assert parameters[2]["name"] == "archived"
        assert "SearchFilter" not in openapi["components"]["schemas"]

    def test_query_directive_on_crud(self) -> None:
        test_input = """\
        type Project {
          name: String! @query
          description: String
          creation_by: String @readOnly @query
          creation_date: Date @readOnly @query
          last_update_by: String @readOnly @query
          last_update_date: Datetime @readOnly
          meta_inf: Object
        }
        """

        openapi = wrapper_generate(test_input)

        parameters = openapi["paths"]["/projects"]["get"]["parameters"]
        assert len(parameters) == 4
        assert parameters[0]["name"] == "filter"
        assert "name" in parameters[0]["schema"]["examples"][0]
        assert "creation_by" in parameters[0]["schema"]["examples"][0]
        assert "creation_date" in parameters[0]["schema"]["examples"][0]
        assert "last_update_by" in parameters[0]["schema"]["examples"][0]
        assert parameters[1]["$ref"] == "#/components/parameters/cursor"
        assert parameters[2]["$ref"] == "#/components/parameters/limit"
        assert parameters[3]["$ref"] == "#/components/parameters/count"
