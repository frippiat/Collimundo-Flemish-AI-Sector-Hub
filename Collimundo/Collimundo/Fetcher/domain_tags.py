from cosmos_db.collimundo_database import GremlinGraphManager
import os
import json
import ast

class domain_tags:
    def __init__(self):
        self.cosmos = GremlinGraphManager()
        # Open the text file in read mode
        with open('./input/domain_tags.txt', 'r') as file:
            # Read the entire contents of the file into a string
            self.domain_tags = ast.literal_eval(file.read())

    def add_to_database(self):
        for domaintag in self.domain_tags:
            if not self.cosmos.is_vertex_in_graph({'id' : "domain_" + domaintag}):
                data = {'id' : "domain_" + domaintag, 'name' : domaintag, 'actor' : 'domain'}

                #step 4: -> store in file
                file_path = os.path.abspath("data/" + domaintag + ".json")

                with open(file_path, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.flush

        #add them to the data base
        self.cosmos.write_to_graph()

    def add_name_lower(self):
        for domaintag in self.domain_tags:
            self.cosmos.submit_query("g.V().has(\"domain\", \"name\"," + domaintag+").add()")

    def add_domain_tag(self, tag):
        self.domain_tags.append(tag)

    def delete_domain_tag(self, tag):
        self.domain_tags.remove(tag)

    def set_domain_tags(self, tags):
        self.domain_tags = tags

    def get_domain_tags(self):
        return self.domain_tags


if __name__=="__main__":
    domain = domain_tags()
    domain.add_to_database()
    #database = GremlinGraphManager()
    #database.write_to_graph()


