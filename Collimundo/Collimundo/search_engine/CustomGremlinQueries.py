
import json

try:
    from .Exceptions import CouldNotRetrieveResult
except (ModuleNotFoundError, ImportError):
    from Exceptions import CouldNotRetrieveResult

class CustomGremlinQueries:
    """! Class used to execute custom Gremlin queries
        Tries to find company names in the prompt and returns the corresponding company ids and linked companies.
    """
    def __init__(self, azure_connection, ranker, debug):
        """! Constructor

        @param azure_connection: The AzureCommunication object
        @param ranker: The ranker object
        @param debug: Debug mode
        """

        self.debug = debug
        self.azure_connection = azure_connection
        self.ranker = ranker
        self.blacklist = [
            "the",
            "of",
            "in",
            "a",
            "an",
            "and",
            "or",
            "is",
            "are",
            "it",
            "its",
            "to",
            "for",
            "with",
            "on",
            "by",
            "at",
            "as",
            "be",
            "from",
            "that",
            "this",
            "which",
            "when",
            "where",
            "who",
            "how",
            "why",
            "it's",
            "i",
        ]

    def get_database_result(self, prompts):
        """! Function used to get the database result
        
        @param prompts: The prompts
        @return: The results
        """

        try:
            return self.azure_connection.make_request(prompts, write_prompts=False)
        except CouldNotRetrieveResult as e:
            print(f"""----------------------
                        ERROR: could not retrieve results
                        Reason: {e}
                    ----------------------""")
            return []

    def get_entity_info_list(self, ids):
        """! Function used to get the entity info list

        @param ids: The ids
        @return: The results
        """
        prompts = [f"g.V().has('id', '{_id}').limit(1)" for _id in ids]
        results = {
            i[0]["id"]: i[0] for i in self.get_database_result(prompts)
        }
        return results

    def get_base_companies_ids(self, query):
        """! Function used to get the base companies ids

        @param query: The query
        @return: The results
        """

        # prompts = [
        #     f"g.V().has('name_lower', '{name}').values('id').limit(1)"
        #     for name in query.split(" ")
        #     if name.lower() not in self.blacklist and len(name) >= 3  # vb ML6
        # ]
        prompts = [
            f"g.V().has('name_lower', '{query}').values('id').limit(1)"
        ]  # only full query
        results = [
            i[0] for i in self.get_database_result(prompts) if len(i) > 0
        ]
        return results

    def get_connected_companies_via_domain(self, ids, filters):
        """! Function used to get the connected companies via domain.

        @param ids: The ids
        @param filters: The filters
        @return: The results
        """

        prompts = [
            f"g.V().has('id', '{_id}').as('source_id')\
.both().hasLabel('domain').as('domain')\
.both().not(where(eq('source_id'))){self.get_filter_query_part(filters)}.as('linked_id')\
.select('source_id', 'domain', 'linked_id')\
.by(values('id'))\
.by(values('name'))\
.by(values('id'))\
.dedup()"
            for _id in ids
        ]
        print(prompts)
        results = self.get_database_result(prompts)
        return results

    def get_connected_companies_via_external(self, ids, filters):
        """! Function used to get the connected companies via intermediate entities

        @param ids: The ids
        @param filters: The filters
        @return: The results
        """

        prompts = [
            f"g.V().has('id', '{_id}').as('source_id')\
.both().hasLabel('implementor', 'investor', 'external', 'research',\
'university', 'individual').as('intermediate_id')\
.both().not(where(eq('source_id'))){self.get_filter_query_part(filters)}.as('linked_id')\
.select('source_id', 'intermediate_id', 'linked_id')\
.by(values('id'))\
.dedup()"
            for _id in ids
        ]
        results = self.get_database_result(prompts)
        return results

    def get_filter_query_part(self, filters):
        """! Function used to get the filter query part. Part of the query that does the filtering.

        @param filters: The filters
        @return: The results
        """

        if filters:
            actor_filter = '\', \''.join(filters)
            actor_filter = f".has('actor', within('{actor_filter}'))"
        else:
            actor_filter = ""
        return actor_filter

    def extract_companies_and_connected(self, query, filters=[]):
        """! Function used to extract companies and connected companies

        @param query: The query
        @param filters: The filters
        @return: The results
        """

        # get all connected
        base_companies = self.get_base_companies_ids(query)

        # no company matched the query
        if not base_companies:
            return {
                "base_companies": [],
                "links": [],
                "info": [],
            }

        # save custom function call for later filter application
        self.azure_connection.save_custom_query_exec("extract_connected", json.dumps(base_companies))

        return self.extract_connected(base_companies, filters)


    def extract_connected(self, base_companies, filters=[]):

        """! Function used to extract connected companies

        @param base_companies: The base companies
        @param filters: The filters
        @return: The results
        """

        print("base_companies:", base_companies, "filters:", filters)

        connected_companies_via_domain = self.get_connected_companies_via_domain(
            base_companies, filters
        )
        connected_companies_via_external = self.get_connected_companies_via_external(
            base_companies, filters
        )

        company_ids_to_search = base_companies.copy()
        company_ids_set = set(base_companies)
        company_links = {}

        # via domain
        for company in connected_companies_via_domain:
            if company == []:
                continue
            for link in company:
                _id = link["linked_id"]
                _domain = link["domain"]
                _link_obj = {
                    "link": link,
                    "type": "domain",
                }
                # Add company to search prop later
                if (_id) not in company_ids_set:
                    company_ids_to_search.append(_id)
                    company_ids_set.add(_id)
                # New domain
                if (_domain) not in company_links:
                    company_links[_domain] = {_id: _link_obj}
                # Add to domain
                if (_id) not in company_links[_domain]:
                    company_links[_domain][_id] = _link_obj

        # via intermediate entities
        for company in connected_companies_via_external:
            if company == []:
                continue
            for link in company:
                _id = link["linked_id"]
                _iter = link["intermediate_id"]
                _link_obj = {
                    "link": link,
                    "type": "partner",
                }
                # Add company to search prop later
                if (_id) not in company_ids_set:
                    company_ids_to_search.append(_id)  # needed
                    company_ids_set.add(_id)
                # Add intermediate to search prop later
                if (_iter) not in company_ids_set:
                    company_ids_to_search.append(_iter)  # needed
                    company_ids_set.add(_iter)
                 # New partner
                if (_iter) not in company_links:
                    company_links[_iter] = {_id: _link_obj}
                # Add intermediate link
                if (_id) not in company_links[_iter]:
                    company_links[_iter][_id] = _link_obj

        # request all data
        company_info = self.get_entity_info_list(company_ids_to_search)

        return {
            "base_companies": base_companies,
            "links": company_links,
            "info": company_info,
        }


    def execute_filtered_function(self, function_name, function_param, filters):
        """! Function used to execute a filter operation on a previously saved function

        @param function_name: The function name
        @param function_param: The function parameter
        @param filters: The filters

        @return: The results
        """
        return eval(f"self.{function_name}({function_param}, {filters})")
