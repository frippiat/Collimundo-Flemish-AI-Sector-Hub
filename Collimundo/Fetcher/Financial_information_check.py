from collimundo_database import GremlinGraphManager
from Financial_information import Financial_source
import json
import datetime

class Financial_check:
    def __init__(self):
        pass
    def check_financials(self):
        #Initialize Staatblad and GremlinGraphManager
        Staatsblad = Financial_source()
        databaseManager = GremlinGraphManager()

        #Query for the Cosmos DB to retrieve all the implementors in the DB
        query = "g.V().has('actor','implementor')"
        out = databaseManager.submit_query(query)
        # print(out[0][0]['id'])

        for implementor in out:

            #Get the VAT of the implementor
            try:
                vat = implementor[0]["properties"]["vat"][0]["value"]
            except:
                vat =''
                break

            #Get the financials of the implementor
            try:
                financial = implementor[0]["properties"]["financial"][0]["value"]
                financial = json.loads(financial)
            except:
                financial = '{}'

            financial_staatsblad = Staatsblad.StaadsbladMonitor(vat)["financial"]
            financial_staatsblad_json = json.dumps(financial_staatsblad)

            if (len(financial) != len(financial_staatsblad)):
                query_implementor = f"g.V().has('id','{implementor[0]['id']}')"
                out_implementor = databaseManager.submit_query(query_implementor)
                print(out_implementor[0][0]['id'])
                query_implementor_update = f"g.V().has('id','{implementor[0]['id']}').property('financial', '{financial_staatsblad_json}')"
                databaseManager.submit_query(query_implementor_update)
        databaseManager.close()       
if __name__ == "__main__":
    current_time = datetime.datetime.now()
    print(f"Financial check started at {current_time}")
    financial = Financial_check()
    financial.check_financials()
    current_time = datetime.datetime.now()
    print(f"Financial check ended at {current_time}")