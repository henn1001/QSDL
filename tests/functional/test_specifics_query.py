from tests import wrapper_generate


class TestSpecificsQuery:
    """Test specific functionality."""

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

        assert parameters[0]["schema"]["properties"]["name"]["type"] == "string"
        assert parameters[0]["schema"]["properties"]["creation_by"]["type"] == "string"
        assert parameters[0]["schema"]["properties"]["creation_date"]["type"] == "string"
        assert parameters[0]["schema"]["properties"]["last_update_by"]["type"] == "string"

        assert parameters[1]["$ref"] == "#/components/parameters/cursor"
        assert parameters[2]["$ref"] == "#/components/parameters/limit"
        assert parameters[3]["$ref"] == "#/components/parameters/count"
