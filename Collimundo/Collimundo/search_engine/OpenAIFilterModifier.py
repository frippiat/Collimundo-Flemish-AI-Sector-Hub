
class OpenAIFilterModifier():
    """! Class to modify the response of the OpenAI API by adding filters to the prompts.
    """

    def __init__(self):
        pass

    def add_type_filter(self, response, type_list):
        type_str = ""
        for type in type_list:
            type_str += "'" + type + "',"
        type_str = type_str[:-1]

        prompts = []

        for prompt in response:

            parts = prompt.split(".")
            # check if before last part is .limit()
            if parts[-1].startswith("limit("):
            # if so place it before .limit() that else before .dedup()
                prefix = ".".join(parts[:-1])
                suffix = "." + ".".join(parts[-1:])

            # else just add it to the end
            else:
                prefix = ".".join(parts[:])
                suffix = ""

            prompt = prefix + ".has('actor', within(" + type_str + "))"  + suffix

            prompts.append(prompt)

        return prompts