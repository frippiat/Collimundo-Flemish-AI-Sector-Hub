import requests
import time
try:
    from Collimundo.Fetcher.keystructure import keymaster
except:
    from keystructure import keymaster

# Fetcher will have a lot of id, key pairs and can switch between them to go around the 100 requests per day limit
class Financial_source:
    def __init__(self, information=["startdate", "EIGEN VERMOGEN",  "Brutomarge",  "Winst (Verlies) van het boekjaar"]):
        self.keymaster = keymaster()
        if not isinstance(information, list):
            assert "Information needed from this source should be passed by a list!"

        self.information = information #a lot of information, only ask the source what we really need

    def get_information(self):
        return self.information

    def set_information(self, information):
        if not isinstance(information, list):
            assert "Information needed from this source should be passed by a list!"
        self.information = information

    def add_information(self, information): #if extra information is needed from this source, input:
        if not isinstance(information, list):
            information = [information]
        self.information.extend(information)

    def delete_information(self, information): #if less information needed
        if information in self.information:
            self.information.remove(information)


    def StaadsbladMonitor(self, VAT):
        params = {
            "vat": VAT,
            "est": "1",
            "fin": "1",
            "apikey":  self.keymaster.get_financial()[0],
            "accountid": self.keymaster.get_financial()[1]
        }

        url = "https://www.staatsbladmonitor.be/sbmapi.json"
        response = requests.get(url, params=params)

        ans = {'financial' : {}}
        print("going in?")
        if response.status_code == 200:
            print("yes")
            all_data = response.json()['data']
            print(all_data)
            #basic information
            ans['zipcode'] = all_data["mainaddress"]['zipcode']
            ans['street'] = all_data["mainaddress"]['street']
            ans['housenumber'] = all_data["mainaddress"]['housenumber']
            ans['city'] = all_data["mainaddress"]['city']
            ans['start date'] = all_data["establishments"][0]['startdate']

            # one year at a time: return a list of lists [[startdate, {dictionary of information}]]
            for year in all_data["annualaccounts"]:
                startdate = year["startdate"]
                values = {}
                for element in year["keyvalues"]:
                    if element["description"] in self.information:
                        values[element["description"]] = element["value"]

                ans['financial'][startdate] = values

        else:
            print(f"Fail: {response.status_code}")
            print(response.text)
        time.sleep(1)
        return ans


if __name__=="__main__":
    test = Financial_source()
    print(test.StaadsbladMonitor('0732698705'))