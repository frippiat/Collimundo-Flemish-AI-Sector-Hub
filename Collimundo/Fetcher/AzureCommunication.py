import openai
from openai.lib.azure import AzureOpenAI
from keystructure import keymaster
import time

class AzureOpenAICommunication:
    def __init__(self, model = "Scraping-assistant"):
        self.keymaster = keymaster()
        self.client = AzureOpenAI(
            azure_endpoint=self.keymaster.endpoint,
            api_key=self.keymaster.openaikey,
            api_version=self.keymaster.api_version
        )

    def communicate(self, system_content,new_message, debug=False, history=[]):
        "get result of sending a new message to openai with a given history"
        message_text = [{"role": "system", "content": system_content}]

        for element in history:
            message_text.append(element)

        message_text.append({"role" : "user", "content" : new_message})

        try:
            completion = self.client.chat.completions.create(
                model=self.keymaster.scraping_model,
                messages=message_text,
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
        except openai.APITimeoutError:
            if self.debug:
                print("Timeout occurred, let's try that again:")
                time.sleep(10)
                return self.communicate(system_content, new_message, debug=debug, history=history)
        if debug:
            print(completion.choices[0].message.content)
        #only 1000 Tokens per minute..
        time.sleep(60)
        return completion.choices[0].message.content

