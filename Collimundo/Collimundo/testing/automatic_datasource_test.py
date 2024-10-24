from Collimundo.Fetcher.Financial_information import Financial_source

def test_api():
    f = Financial_source()
    #this is the VAT of the company techwolf
    assert f.StaadsbladMonitor("0702852201") != None, "Financial information source isn't available!!"

