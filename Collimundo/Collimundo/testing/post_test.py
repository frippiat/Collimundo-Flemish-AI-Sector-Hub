from Collimundo.search_engine.GremlinGraphManager import GremlinGraphManager
from pathlib import Path

"""last thing to do is clear up everything added during the testing processes!"""

def test_clear():
    # Determine the script directory
    script_dir = Path(__file__).resolve().parent

    # Path to the unique_id.txt file
    unique_id_file = script_dir / 'unique_id.txt'

    # Ensure the file exists before trying to read it
    assert unique_id_file.exists(), "no unique id file to delete the subsystem!"

    # Get unique id from the file
    with unique_id_file.open('r') as f:
        unique_test_id = f.read().strip()

    g = GremlinGraphManager()

    # Delete everything starting with Collimundo_test_team in the database
    ids = [f"CollimundoTest_company_{unique_test_id}", f"UniversityTest_{unique_test_id}"]
    for id in ids:
        g.delete_vertex(id)

    # drop the vacancy
    query = f"g.V().hasLabel('vacancy').has('description',  TextP.endingWith('{unique_test_id}')).drop()"
    g.submit_query(query)
