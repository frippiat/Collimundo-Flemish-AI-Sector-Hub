class keymaster():
    #here you can change all keys used for connections to openai, cosmos, staatsbladmonitor, ...
    def __init__(self):
        self.openaikey = "88735801ac7e4448a6d974870177b127"
        self.endpoint = "https://collimundo2.openai.azure.com/"
        self.api_version = "2024-02-01"
        self.financial =  [
    ("91c5d043-16c7-42c2-b8dc-cb94a289bf77", 2929400),
    ("36176914-6a40-4850-b5e2-cad08d43b01e", 2929602),
    ("077141f6-5d52-4db1-aea5-54ec5e710788", 2929703),
    ("5feaf9d1-7255-4c83-ba1b-4b461c72ebe2", 2929804),
    ("9dcef339-2cab-42cb-ad41-9dfa6430509c", 2929905),
    ("1f74c6e3-408c-409f-9c4e-2be379030c59", 2930006),
    ("34143efa-d194-4960-8c9c-e5fd03763eb4", 2930107),
    ("7c432f73-a7ca-4d7a-94f7-cf5e99331164", 2930208),
    ("497c554a-8842-4bca-a889-242e029893fc", 2930309),
    ("e459555a-abd7-43d0-adb4-e476ab972692", 2930612),
    ("b82e9a21-cbc3-437f-92e2-a6f97e45ca51", 2930713),
    ("d9218ff7-3df8-467f-9cce-769a1fa9a3be", 2930814),
    ("03e69848-e790-45aa-88e3-f292c7df9171", 2930915),
    ("e9c519f4-1dfd-4997-95ff-a88d902103c3", 2931016),
    ("e1342884-5393-44ba-8214-114f576a492c", 2931117),
    ("f05cb154-e3fb-414c-8d3f-b2c529466c30", 2931218),
    ("7605264b-f739-457b-b7ac-6835cd2642b4", 2931319),
    ("b7654092-35ae-42e9-a12c-5dbe031f0c48", 2931420),
    ("139829a6-2a98-43fb-ac57-65d29e2f0762", 2931521),
    ("0420f28d-6ed7-4f5a-898b-8ba95570583f", 2931622),
    ("ba71ca6e-f902-4f6f-ac5f-950c4beafd23", 2931723),
    ("b6364ac1-7920-4243-be65-a565f6d6b348", 2931824),
    ("983a45c4-6c76-482e-aa79-077e02c7edd3", 2931925),
    ("f42a3381-86d8-46eb-9da2-31ee19f2306f", 2932026),
    ("c6b0f661-9589-47b6-927b-397df14e717b", 2932127),
    ("84e42fd2-0723-4a5f-a407-e0603045bc3a", 2932228),
    ("ecaeda7d-c997-46e0-8d1e-234df286c62c", 2932329),
    ("0c1ba9ab-a171-4854-8d23-c50f8f9882ff", 2932430),
    ("bfbf8195-9241-4365-bf13-0dc5998f4972", 2932531),
    ("bc3262c2-743c-4200-ac14-445259e33a9d", 2932632),
    ("6586a1a0-8379-4e9b-9167-c38e6144d0e4", 2932733),
    ("b85eb2b1-84f4-44f3-8be2-249d587b95ac", 2932834),
    ("ea51ca59-ddaa-4bb6-afcd-69d695793ec9", 2932935),
    ("a41992ef-77a9-4728-b92e-81e43ba32fdf", 2933036),
    ("df56dc23-15a0-415e-a9aa-f6ef73e78677", 2933137),
    ("1f2c01da-7e36-4cbd-9c79-8cc58a59af2b", 2933238),
    ("de6da5e4-4149-4982-8a44-ac7c2105bbd4", 2933339),
    ("9a6bc3b9-29d5-4d71-b7da-fc2738641307", 2933440),
    ("b8980536-18fd-42b5-a0ca-fdb1eb17840b", 2933541),
    ("e61e85d7-c02f-4692-bed1-38c8116b5fd4", 2933642),
    ("cb6b210e-7321-4e1e-8428-f9fe464b6cb3", 2933743),
    ("b2ad8950-b6e9-4361-ac8e-b037fd5a8191", 2968503),
    ("934edae4-19a5-444f-80d6-e0c2f28fffa5", 2968604),
    ("458efcff-cdca-421c-afa2-83cbfa560b56", 2968705),
    ("a83a5afe-57d8-40c0-b81e-6d6482b25921", 2968806),
    ("4b259aef-9bec-4e69-8d44-e0311f63eb9d", 2968907),
    ("5b02a1c8-5b05-401d-b905-1be6e563e259", 2969008),
    ("7264e473-a58a-4913-bc52-36b952f37ac8", 2969109),
    ("d34a5050-ece0-411f-83db-159dc26e7093", 2969210),
    ("d55b8e26-26f2-4e11-a3f7-b2bc71e9e4d5", 2972341),
    ("a7e9c00a-3f57-4d61-9a79-3d154990b76c", 2972442),
    ("7b552c3a-6606-47a2-a4a9-a94cbe3c91e1", 2972543),
    ("9568193f-291f-4842-af22-088e05ecf7c1", 2972644),
    ("7c782a65-36c6-4bd0-9f58-01c20f684ea5", 2972745),
    ("7a3b337b-c55b-40f5-a4a7-767095e02e10", 2972947),
    ("18e3e663-31f0-47b9-a101-61b49186110d", 2973048),
    ("ff087adc-601b-4bda-9d74-fb5cd647cf5d", 2973149),
    ("3f6419fa-da70-4356-88dc-86ff255a4e48", 2973250),
    ("58f408da-9365-46c1-8ce6-84b4b1cb07c4", 2973351),
    ("22ba0edc-18f4-457f-abba-b637f1090b7e", 2973452),
    ("bdd68cb5-c004-4cae-a2af-72ec56abd19d", 2973553),
    ("2bb51bc4-a290-415e-83ba-e76ea236f43f", 2973654),
    ("18015a9f-1380-4581-8ba9-0c39a803a7d4", 2973755),
    ("870f4c58-d062-4fdc-a901-1d80e3689c21", 2973856),
    ("88d63f58-5160-4ec3-b191-5be1b4af9034", 2973957),
    ("0fc18960-e5a0-4d11-978e-b5d9718d0260", 2974058),
    ("06c94a50-6974-49e9-8932-82cbca0edbc8", 2974159),
    ("a8c314f5-0aed-4775-ba7b-50f1e50315fe", 2974260),
    ("21638889-360f-45d6-ab0c-5f7bae1c6a12", 2974361),
    ("7476b5c8-9af4-45d4-a6c3-d00aa66c8094", 2974462),
    ("3e57cf8a-201e-49c3-bd7f-45b662df05c4", 2974563),
    ("c2eaeda9-11b1-4902-a9e5-c8e2b9953cf5", 2974664),
    ("bece9175-4261-4d90-b8c2-5ba4c051f7e6", 2974765),
    ("6b09ce1f-7415-4cbd-8c68-077ed1d5fc94", 2974866),
    ("9120f0a9-c5ac-400b-a21a-8ba915736c20", 2974967),
    ("dd9b6d5d-08af-4b41-b83f-9151b6ecd3fe", 2975068),
    ("402996bf-3894-4c49-8447-1e35c4aad989", 2975169),
    ("5ed4ccad-bb52-4854-8be6-69eb10f353e1", 2975270),
    ("86379695-2b76-4b7f-b88e-87885544dc00", 2975371),
    ("47078efd-6665-468e-ba15-2359e003821f", 2975472),
    ("375a1a10-3ca1-447a-800c-501b5cebef86", 2975573),
    ("02a81245-0da8-4d8b-bd80-e442859e7bc7", 2975674),
    ("7005ca81-6159-450c-abeb-0ef4cd58592c", 2975775),
    ("09264642-a4de-4b1a-841b-efd46fc17bf6", 2975876),
    ("1e92e877-fe79-4dcf-bc86-6b48acbdd5b6", 2975977),
    ("e1dd50fd-1834-43ad-809b-7fa39564d987", 2976078),
    ("94b2144e-fc54-45f3-9bb1-4150f43b5ed4", 2976280),
    ("804f72b1-e74d-4542-a995-a4ff277dbbb6", 2976381)
]
        self.scraping_model = "Scraping-assistant"

        # of some keys have a day limit
        self.requests = 0
        self.current_key = 0

    def get_financial(self):
        self.requests += 1
        if self.requests == 37:
            self.current_key += 1 % len(self.financial)
            self.requests = 0
        return self.financial[self.current_key]

    def set_key(self, key_name, value):
        #set the key based on the name of the attribute
        if hasattr(self, key_name):
            setattr(self, key_name, value)
        else:
            raise AttributeError(f"keymaster does not yet have an attribute to take care of the key {key_name}!")

if __name__=="__main__":
    key = keymaster()
    key.set_key("openaikey", "kaas")
    print(key.openaikey)
    print(key.get_financial())

