import re

# import Levenshtein


class QuerySyntaxChecker:
    """! Class to check the syntax of a query
    """
    def __init__(self, debug):
        self.basicSyntaxLibrary = {
            "textContaining": "containing",
        }
        # self.basicSyntaxLibrary = [
        #     ".",
        #     ",",
        #     "(",
        #     ")",
        #     "__",
        #     "'",
        #     '"',
        #     "g",
        #     "V",
        #     "hasLabel",
        #     "has",
        #     "or",
        #     "containing",
        #     "limit",
        #     "valueMap",
        #     # to be expanded
        # ]
        self.debug = debug

    def check(self, query):
        """! Function used to check the syntax of a query

        @param query: The query to check

        @return: The checked query
        """
        if isinstance(query, list):
            # for list of queries
            output = []
            for q in query:
                output.append(self.check(q))
            return output
        else:
            # first basic word checks
            query = self.performCheck(query)
            # finaly return
            return query

    def performCheck(self, query):
        """! Function used to perform the check

        @param query: The query to check

        @return: The checked query
        """
        query = self.allSingleQuotes(query)
        query = self.basicSyntaxCheck(query)
        query = self.checkSpecificStatments(query)
        return query

    def allSingleQuotes(self, query):
        """! Function used to replace all double quotes with single quotes

        @param query: The query to check

        @return: The checked query
        """
        return query.replace('"', "'")

    def basicSyntaxCheck(self, query):
        """! Function used to check the basic syntax of a query

        @param query: The query to check

        @return: The checked query
        """
        input_objs = re.findall(r"[\w']+|[\(\),.]", query)
        for word in input_objs:
            # # search params are between qoutes so these wont be changed
            # if word[0] == "'" or word[0] == '"':
            #     continue
            # # if not in library -> replace by closest word
            # if word not in self.basicSyntaxLibrary and not word.isdigit():
            #     replacement = self.getClosestWord(word)
            #     query = query.replace(word, replacement)
            if word in self.basicSyntaxLibrary:
                query = query.replace(word, self.basicSyntaxLibrary[word])
        return query

    # def getClosestWord(self, word):
    #     closest_word = None
    #     min_distance = float("inf")
    #     for w in self.basicSyntaxLibrary:
    #         distance = Levenshtein.distance(word, w)
    #         if distance < min_distance:
    #             min_distance = distance
    #             closest_word = w
    #     return closest_word

    def checkSpecificStatments(self, query):
        """! Function used to check the specific statements of a query

        @param query: The query to check

        @return: The checked query
        """
        commands = query.split('.')
        for i in range(len(commands)):
            command = commands[i]

            # HAS - filter has statements
            if (command.startswith("has(")):
                parts = command[4:-1].split(', ')
                parts_len = len(parts)


                # Style - label
                if (parts_len == 1):
                    pass

                else:
                    if parts[1].startswith("within"):
                        parts = [parts[0], ', '.join(parts[1:])]
                        parts_len = 2

                    # Style - attr : value
                    if (parts_len == 2):
                        attr, value = parts
                        if (attr == "'name'"):
                            attr = "'name_lower'"
                            value = value.lower()
                        parts = [attr, value]

                    # Style - label, attr : value
                    elif (parts_len == 3):
                        pass

                    # Style - wrong -> label, attr : value
                    elif (parts_len == 4):
                        parts = parts[1:]

                command = "has(" + ", ".join(parts) + ")"

            # Join parts
            commands[i] = command
        
        # DEDUP - always end with dedup
        if (commands[-1] != "dedup()"):
            commands.append("dedup()")

        return '.'.join(commands)


if __name__ == "__main__":
    syntaxCheck = QuerySyntaxChecker(True)
    res = syntaxCheck.check(["g.V().has('actor','domain').has('name', within('Hardware','Embedded Systems','Healthcare')).in()"])
    print(res)
    