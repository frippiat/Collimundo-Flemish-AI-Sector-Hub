from pathlib import Path
from uuid import uuid4
from Collimundo.search_engine.GremlinGraphManager import GremlinGraphManager
import os
import json
import time
import pytest
"""In this file, we will set up the test environment for the other testing code. 
"""

def test_uuid_generation():
    unique_id = uuid4()
    with open('unique_id.txt', 'w') as f:
        f.write(str(unique_id))
        # get unique id:
    with open('unique_id.txt', 'r') as f:
        unique_test_id = f.read().strip()
    assert unique_test_id ==str(unique_id), "something wrong with the unique id"

def test_database_connectivity():
    #get unique id:
    with open('unique_id.txt', 'r') as f:
        unique_test_id = f.read().strip()

    # database reachability
    g = GremlinGraphManager()
    #quick check if no one deleted or database:
    assert g.read_full_graph() != None, "oops, someone deleted our database or the read_full_graph doesn't work!"

    # add a test json
    id = f"CollimundoTest_company_{unique_test_id}"
    data = {"id" : id, "name" : f"CollimundoTest_{unique_test_id}", "name_lower" : f"collimundotest_{str(unique_test_id).lower()}", "actor" : "implementor"}

    # Relative path to the file t
    relative_file_path = os.path.join('..', 'search_engine', 'data_for_database', 'Collimundotest.json')
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the target file
    absolute_path = os.path.join(script_dir, relative_file_path)

    # Write data to the JSON file
    with open(absolute_path, 'w') as file:
        json.dump(data, file, indent=4)
        file.flush()


    assert os.path.exists(absolute_path), f"File not found: {absolute_path}"


    #write the entity to the database (=test the write to database function)
    g.write_to_graph()


    #first check if the get_vertex_by_id function works, this entity should thus always be in the database!!!!
    assert g.get_vertex_by_id("collimundo.com") != None, "database is deprecated or get_vertex_by id fails!"

    #check if the entity is in the graph to know the write_to_graph function works
    assert g.get_vertex_by_id(id) != [], "something went wrong with writing to the database!!"

    #test if we can submit a valid query too
    result = g.submit_query(f"g.V('{id}')")
    assert result[0][0]['id'] == id, "something went wrong with submitting a valid gremlin query!!!"
    #test if changing database will cause an error
    g.submit_query(f"g.V('{id}').drop()", read_only=True)
    assert g.get_vertex_by_id(id) != [], "danger! Injections possible with search engine!"

    #test the change property function
    g.change_properties(id, {"test": "test"})
    properties = g.get_vertex_by_id(id)[0]["properties"]
    assert properties["test"][0]["value"] == "test", "something wrong with adding a property!"
    assert properties["dirty"][0]["value"] == 1, "Dirty bit was not set when a change occured"

    #delete the vertex again
    g.delete_vertex(id)
    time.sleep(2) #asynchroon deletion takes some time
    result = g.get_vertex_by_id(id)

    assert result == [], "something went wrong with deleting a vertex!!"
    assert not(g.is_vertex_in_graph(data)), 'something went wrong with deleting a vertex!!'

    #and add it again with the add vertex function
    g.add_vertex("implementor", id = id, name = f"CollimundoTest_{unique_test_id}", name_lower = f"collimundotest_{str(unique_test_id).lower()}")
    assert g.is_vertex_in_graph(data), 'something went wrong with adding a vertex!!'

    #check the find_vertex_id function
    assert g.find_vertex_id({"name" : f"CollimundoTest_{unique_test_id}", "name_lower" : f"collimundotest_{str(unique_test_id).lower()}", "actor" : "implementor"})[0] == id, "something went wrong with finding the id based on properties!"

    #add a edge (first add another property)
    id_2 = f"UniversityTest_{unique_test_id}"
    data2 = {"actor" :"university", "id" : id_2, "name":id_2, "name_lower":"universitytest"}
    g.add_vertex("university", id = id_2, name=f"UniversityTest_{unique_test_id}", name_lower="universitytest")
    assert g.is_vertex_in_graph(data2), "something went wrong with adding a vertex!!"

    #add the edge
    g.add_edge(id, "uni_alumni", id_2)

    #test if add edge and find edge work
    assert g.find_edge_id_by_vertices(id, "uni_alumni", id_2) != None, "Adding/retrieving edges fails!"

    # delete the edge
    g.delete_edge(g.find_edge_id_by_vertices(id, "uni_alumni", id_2)[0])
    time.sleep(2) #asyncr takes some time
    assert g.submit_query(f"g.V().has('id', '{id}').both('uni_alumni')") == [], "deleting edges fails!"

    ##### finally: create here the full test environment, currently: university, company, edge in between them
    ## make sure to delete them in the post test file!!!!!!!!!!!!!
    #add the edge
    g.add_edge(id, "uni_alumni", id_2)

    #create job openings
    g.add_vertex('vacancy', title='Test Manager', description=f'Test Manager for CollimundoTest_{unique_test_id}')




