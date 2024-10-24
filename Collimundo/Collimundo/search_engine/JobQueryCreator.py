

class QueryCreator:
    """! Class used to create custom queries for the search engine
    """

    def __init__(self):
        self.words_blacklist = ["the", "de", "of", "van", "in", "in", "a", "een", "an", "een", "and", "en", "or", "of", "is", "is", "are", "it", "het", "its", "zijn", "to", "naar", "for", "voor", "with", "met", "on", "op", "by", "door", "at", "bij", "as", "als", "be", "is", "from", "uit", "that", "dat", "this", "dit", "which", "welke", "when", "wanneer", "where", "waar", "who", "wie", "how", "hoe", "why", "waarom", "it's", "i", "ik"]

    # function to guide the custom query creation process
    def create_query(self, input_string):
        """! Function used to guide the custom query creation process

        @param input_string: The input string

        @return: The custom queries
        """

        input_string = input_string.lower()

        prompts = {}

        # 1: make prompts for situation where input_string is a company name
        prompts["company"] = self.make_company_name_query(input_string)

        # 2: make prompts for situation where input_string is a title
        prompts["title"] = self.make_title_query(input_string)

        # 3: make prompts for situation where input_string contains a place (city, zipcode or country)
        prompts["place"] = self.make_place_query(input_string)

        # 4: make prompts for situation where input_string contains words in the description
        prompts["description"] = self.make_description_query(input_string)

        return prompts

    # function to create a gremlin query in the case that the search query is the name of a company
    def make_company_name_query(self, name):
        """! Function used to create a gremlin query in the case that the search query is the name of a company

        @param name: The name of the company

        @return: The gremlin query
        """
        return [f"g.V().has('name_lower', '{name}').in().has('label', 'vacancy')"]

    # function to create a gremlin query in the case that the search query is part of a job title
    def make_title_query(self, title):
        """! Function used to create a gremlin query in the case that the search query is part of a job title

        @param title: The title of the job

        @return: The gremlin query
        """

        title_parts = title.split(' ')
        title_prompt = f"g.V().has('label', 'vacancy').and("
        for i, part in enumerate(title_parts):
            if i != 0:
                title_prompt += ","
            part = part.strip()[1:]
            title_prompt += f"has('title', containing('{part}'))"
        title_prompt += ")"
        return [title_prompt]

    # function to create a gremlin query in the case that the search query contains a place
    def make_place_query(self, input_string):
        """! Function used to create a gremlin query in the case that the search query contains a place

        @param input_string: The input string

        @return: The gremlin query
        """

        place_parts = input_string.split()

        # city
        city_prompt = f"g.V().has('label', 'vacancy').or("
        for i, part in enumerate(place_parts):
            if i != 0:
                city_prompt += ","
            part = part.strip()[1:]
            city_prompt += f"has('city', containing('{part}'))"
        city_prompt += ")"

        # zipcode
        zip_prompt = f"g.V().has('label', 'vacancy').or("
        for i, part in enumerate(place_parts):
            if i != 0:
                zip_prompt += ","
            part = part.strip()[1:]
            zip_prompt += f"has('zipcode', containing('{part}'))"
        zip_prompt += ")"

        # country
        country_prompt = f"g.V().has('label', 'vacancy').or("
        for i, part in enumerate(place_parts):
            if i != 0:
                country_prompt += ","
            part = part.strip()[1:]
            country_prompt += f"has('country', containing('{part}'))"
        country_prompt += ")"

        return [city_prompt, zip_prompt, country_prompt]

    # function to create a gremlin query in the case that the search query contains part of the description of a job opening
    def make_description_query(self, input_string):
        """! Function used to create a gremlin query in the case that the search query contains part of the description of a job opening

        @param input_string: The input string

        @return: The gremlin query
        """
        description_words = input_string.split(" ")
        description_words = [word[1:] for word in description_words if (word not in self.words_blacklist and len(word) > 4)]
        description_prompt = f"g.V().has('label', 'vacancy').or("
        for i, word in enumerate(description_words):
            if i != 0:
                description_prompt += ","
            description_prompt += f"has('description', containing('{word}'))"
        description_prompt += ")"
        return [description_prompt]


