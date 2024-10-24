from Collimundo.search_engine.embedding import Ranker
import numpy as np
import pytest

"""file to test everything related to embedding!"""

def test_embedding():
    #dependencies
    test = Ranker()

    #embedding test
    assert all(isinstance(x, float) for x in test.get_embedding("this is a test")), "Azure Openai embedding communication fail!"

    #all other elements:
    query = "companies that can help reducing the waste of my food production machines"
    json_list = test.gremlin.submit_query(
        'g.V().has("actor", "domain").has("name", within("Waste Management", "Food")).both("works_on").has("actor", "implementor")')

    json_list = np.array(json_list).flatten()
    sorted = test.rank_on_query(json_list, query)
    #same elements
    assert len(sorted) == len(json_list), "not all elements are included in the sorted list!"
    for element in sorted:
        assert element in json_list, "not all elements are included in the sorted list!"
    #type
    assert isinstance(sorted, list), "should return a sorted list!!"
    assert all(isinstance(x, dict) for x in sorted), "all elements should be of the standard cosmos type!"

    # test if the dirty bit method works as it should
    test.gremlin.change_properties("collimundo.com", {"embedding": "test"}) #after the reordering, embedding shouldnt be equal to test anymore
    json_list = np.array(test.gremlin.submit_query("g.V('collimundo.com')")).flatten()
    sorted = test.rank_on_query(json_list, "pass") #query does not matter
    json_list = np.array(test.gremlin.submit_query("g.V('collimundo.com')")).flatten()
    assert json_list[0]["properties"]["dirty"][0]["value"] == 0, "dirty bit isnt restored to zero!"
    assert json_list[0]["properties"]["embedding"][0]["value"] != "test", "embedding isnt changed!"

