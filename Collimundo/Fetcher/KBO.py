import csv
import shutil
import zipfile
import os
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import time

class KBO:
    def __init__(self):
        pass

    def calculate_counter(self,month, year):
        # Define the reference date
        reference_date = datetime(2023, 11, 1)
        
        # Get the current date
        current_month, current_year = datetime.now().month, datetime.now().year
        
        # Check if the given date is within the valid range
        if year<2023 or year>current_year or (month<11 and year==2023) or (month>current_month and year==current_year) or month>12 or month<0:
            raise ValueError("FILE DOES NOT EXIST ON THE KBO DATABASE")
        
        # Calculate the number of months between the reference date and the given date
        months_difference = (year - reference_date.year) * 12 + (month - reference_date.month)
        
        # Calculate the counter value
        counter = 117 + months_difference
        
        return counter

    def retrieve_zip_file(self,month,year,file_type="update"):
        counter=self.calculate_counter(month, year)
        if(month<10):
            month_str=str(0)+str(month)
        else:
            month_str=str(month)
        url="https://kbopub.economie.fgov.be/kbo-open-data/affiliation/xml/files/KboOpenData_0"+str(counter)+"_"+str(year)+"_"+str(month_str)+"_"+file_type.capitalize()+".zip"
        username = "collimundoking"
        password = "P@ssw0rd1"

        # Send a GET request to the URL with authentication
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        
        zip_file_name='KboOpenData_0'+str(counter)+'_'+str(year)+'_'+str(month_str)+'_'+file_type.capitalize()+'.zip'
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a file in binary write mode and write the content of the response to it
            with open(zip_file_name, 'wb') as f:
                f.write(response.content)
            print("Download successful")
        else:
            print("Failed to download:", response.status_code)
            
        return zip_file_name

    def reduceCSV(self,file, file_type="update",reduction=-1):
        # Define the path to your CSV file
        path_extract=file_type+"/extracted/"+file
        # Define the path to the new CSV file where you'll keep the first "reduction" rows
        path_necessary=file_type+"/necessary/"+file

        # Open the original CSV file for reading
        with open(path_extract, 'r', encoding='utf-8') as original_file:
            # Create a CSV reader object
            csv_reader = csv.reader(original_file)

            # Open the new CSV file for writing, specifying UTF-8 encoding
            with open(path_necessary, 'w', newline='', encoding='utf-8') as new_file:
                # Create a CSV writer object
                csv_writer = csv.writer(new_file)

                # Write the first 200 rows to the new file
                for index, row in enumerate(csv_reader):
                    try:
                        if index < reduction:
                            csv_writer.writerow(row)
                        else:
                            break
                    except UnicodeEncodeError as e:
                        print(f"UnicodeEncodeError occurred at row {index}: {e}")
                        # Optionally, you can choose to skip problematic rows or handle them differently
    def extractFiles(self,month,year,file_list,file_type="update",reduction=-1):
        # Delete the directory and all its contents if it already exists
        if os.path.exists(file_type):
            shutil.rmtree(file_type)
        
        #recreate the directory
        os.makedirs(file_type, exist_ok=True)
        
        # Create a directory if it doesn't exist
        path_extract=file_type+"/"+"extracted"
        os.makedirs(path_extract, exist_ok=True)
        
        # Create a directory if it doesn't exist
        path_necessary=file_type+"/"+"necessary"
        os.makedirs(path_necessary, exist_ok=True)
        
        zip_file=self.retrieve_zip_file(month,year,file_type)
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(path_extract)
        
        if(reduction==-1):
            # Move each file from the source directory to the destination directory
            for root, _, files in os.walk(path_extract):
                for file_name in files:
                    source_file_path = os.path.join(root, file_name)
                    destination_file_path = os.path.join(path_extract, file_name)
                    shutil.move(source_file_path, destination_file_path)
                    if file_name in file_list:
                        destination_file_path_extract = os.path.join(path_necessary, file_name)
                        shutil.move(source_file_path, destination_file_path_extract)
            return
        
        for file_name in file_list:
            self.reduceCSV(file_name, file_type, reduction)
        
        return
    def extractFilesFull(self,month, year, reduction=-1):
        file_list_full_update = ["address.csv", "denomination.csv","contact.csv","establishment.csv","activity.csv"]
        self.extractFiles(month, year, file_list_full_update, file_type="full", reduction=reduction)
        return
    def extractFilesUpdate(self,month, year, reduction=-1):
        file_list_full_update = ["address_insert.csv", "denomination_insert.csv","contact_insert.csv","establishment_insert.csv","activity_insert.csv","establishment_delete.csv"]
        self.extractFiles(month, year, file_list_full_update,file_type="update", reduction=reduction)
        return
    # Function to load CSV files
    def load_csv(self,filename):
        data = []
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data
    # Function to categorize data and construct JSON
    def categorize_full_data(self):
        # Load CSV files
        location="full/necessary/"
        activity_data = self.load_csv(location+'activity.csv')
        address_data =  self.load_csv(location+'address.csv')
        trackID_data =  self.load_csv(location+'establishment.csv')
        denomination_data =  self.load_csv(location+'denomination.csv')
        
        #desired_nace_codes_2003=['72100', '72200', '72210', '72220', '72300', '72400', '72600']
        #desired_nace_codes_2008=['62010', '62020', '62030', '62090', '63110', '63120', '63990']
        desired_nace_codes_2003=[]
        desired_nace_codes_2008=['62010','62020']
        
        # Initialize main JSON dictionary
        main_dict = {}

        # Add in companies that have the desired nacebel codes
        classification_map = {'MAIN': 'main', 'SECO': 'secondary', 'ANCI': 'supporting'}
        for row in activity_data:
            if row['ActivityGroup'] in ['001', '006']:
                id = row['EntityNumber']
                code = row['NaceCode']
                version = row['NaceVersion']
                classification=classification_map.get(row['Classification'])
                if (version=='2003' and code in desired_nace_codes_2003) or (version=='2008' and code in desired_nace_codes_2008):
                    if id not in main_dict:
                        main_dict[id]={}
                        main_dict[id]['activity']={}
                    if classification not in main_dict[id]['activity']:
                        main_dict[id]['activity'][classification]={}
                    main_dict[id]['activity'][classification].setdefault(version, []).append(code)

        #VERVANGEN BIJ IF 1: if (version=='2003' and code in desired_nace_codes_2003) or (version=='2008' and code in desired_nace_codes_2008):            

        #Add in the address of the companies to verify if they are in Flanders or Brussels
        for row in address_data:
            id = row['EntityNumber']
            if id in main_dict:
                if row['TypeOfAddress'] == 'REGO':
                    main_dict[id]['address'] = {
                        'municipality': row['MunicipalityNL'],
                        'zipcode': row['Zipcode'],
                        'street': row['StreetNL'],
                        'streetnumber': row['HouseNumber']
                    }

        # Remove companies that are not from Flanders or Brussels
        for id in list(main_dict.keys()):
            if 'address' in main_dict[id]:
                zipcode = main_dict[id]['address']['zipcode']
                if not zipcode.startswith(('10','11','12','15','16','17','18','19','2', '3', '8', '9')):
                    del main_dict[id]
                    
        #Remove address data as we don't need it yet
        for id in list(main_dict.keys()):
            if 'address' in main_dict[id]:
                    del main_dict[id]['address']
        
        # Give a unique ID per company, to keep track of which companies KBO removes from their database
        for row in trackID_data:
            id=row['EnterpriseNumber']
            if id in main_dict:
                establishment_number= row['EstablishmentNumber']
                main_dict[id]['trackID'] = establishment_number
                
        for row in denomination_data:
            id=row['EntityNumber']
            if id in main_dict:
                establishment_name= row['Denomination']
                main_dict[id]['name'] = establishment_name


        return main_dict

    # Main function
    def retrieve_full_from_CSV_into_JSON(self,output_json_name):
        categorized_data = self.categorize_full_data()
        with open(output_json_name, 'w') as json_file:
            json.dump(categorized_data, json_file, indent=4)

    # Function to categorize data and construct JSON
    def categorize_update_data(self,currentJson):
        # Load CSV files
        location="update/necessary/"
        activity_data = self.load_csv(location+'activity_insert.csv')
        address_data = self.load_csv(location+'address_insert.csv')
        trackID_data = self.load_csv(location+'establishment_insert.csv')
        trackID_data_delete = self.load_csv(location+'establishment_delete.csv')
        denomination_data = self.load_csv(location+'denomination_insert.csv')
        
        #desired_nace_codes_2003=['72100', '72200', '72210', '72220', '72300', '72400', '72600']
        #desired_nace_codes_2008=['62010', '62020', '62030', '62090', '63110', '63120', '63990']
        desired_nace_codes_2003=[]
        desired_nace_codes_2008=['62010','62020']
        
        with open(currentJson, 'r') as file:
            json_data = file.read()
        
        main_dict= json.loads(json_data)

        # Add in companies that have the desired nacebel codes
        classification_map = {'MAIN': 'main', 'SECO': 'secondary', 'ANCI': 'supporting'}
        for row in activity_data:
            if row['ActivityGroup'] in ['001', '006']:
                id = row['EntityNumber']
                code = row['NaceCode']
                version = row['NaceVersion']
                classification=classification_map.get(row['Classification'])
                if (version=='2003' and code in desired_nace_codes_2003) or (version=='2008' and code in desired_nace_codes_2008):
                    if id not in main_dict:
                        main_dict[id]={}
                        main_dict[id]['activity']={}
                    if classification not in main_dict[id]['activity']:
                        main_dict[id]['activity'][classification]={}
                    main_dict[id]['activity'][classification].setdefault(version, []).append(code)

        #VERVANGEN BIJ IF 1: if (version=='2003' and code in desired_nace_codes_2003) or (version=='2008' and code in desired_nace_codes_2008):            

        #Add in the address of the companies to verify if they are in Flanders or Brussels
        for row in address_data:
            id = row['EntityNumber']
            if id in main_dict:
                zipcode = row['Zipcode']
                if row['TypeOfAddress'] == 'REGO':
                    main_dict[id]['address'] = {
                        'municipality': row['MunicipalityNL'],
                        'zipcode': zipcode,
                        'street': row['StreetNL'],
                        'streetnumber': row['HouseNumber']
                    }

        # Remove companies that are not from Flanders or Brussels
        for id in list(main_dict.keys()):
            if 'address' in main_dict[id]:
                zipcode = main_dict[id]['address']['zipcode']
                if not zipcode.startswith(('10','11','12','15','16','17','18','19','2', '3', '8', '9')):
                    del main_dict[id]
                                        
        #Remove address data as we don't need it yet
        for id in list(main_dict.keys()):
            if 'address' in main_dict[id]:
                    del main_dict[id]['address']
        
        # Give a unique ID per company, to keep track of which companies KBO removes from their database
        for row in trackID_data:
            id=row['EnterpriseNumber']
            if id in main_dict:
                establishment_number= row['EstablishmentNumber']
                main_dict[id]['trackID'] = establishment_number
        for row in denomination_data:
            id=row['EntityNumber']
            if id in main_dict:
                establishment_name= row['Denomination']
                main_dict[id]['name'] = establishment_name
        #Remove companies that KBO removed from their own database                                  
        for row in trackID_data_delete:
            establishment_number = row['EstablishmentNumber']
            # Check if the establishment number exists in the main dictionary
            for id in main_dict.keys():
                if 'trackID' in main_dict[id]:
                    if main_dict[id]['trackID'] == establishment_number:
                        del main_dict[id]
                        break
        
        return main_dict


    # Main function
    def retrieve_update_from_CSV_into_JSON(self,input_json_name, output_json_name):
        categorized_data = self.categorize_update_data(input_json_name)
        with open(output_json_name, 'w') as json_file:
            json.dump(categorized_data, json_file, indent=4)
    def ZipToJson(self,month, year, output_json_name, file_type,file_size_reduction=-1):
        if(file_type=="update"):
            self.extractFilesUpdate(month, year ,file_size_reduction)
            self.retrieve_update_from_CSV_into_JSON(output_json_name,output_json_name)
        elif(file_type=="full"):
            self.extractFilesFull(month, year ,file_size_reduction)
            self.retrieve_full_from_CSV_into_JSON(output_json_name)
        return
    
    def get_kbo_implementors(self,month,year):
        if os.path.exists("input/jsonOutputFile.json"):
              self.ZipToJson(month,year,output_json_name="input/jsonOutputFile.json",file_type="update")
        else:   
              self.ZipToJson(month,year,output_json_name="input/jsonOutputFile.json",file_type="full")
              time.sleep(5)
              self.ZipToJson(month,year,output_json_name="input/jsonOutputFile.json",file_type="update")

        with open("input/jsonOutputFile.json", 'r') as json_file:
                data=json.load(json_file)

        implementors = []
        for item in data.items():
                dic={}
                try:
                    dic= {"vat":item[0].replace(".",""),"name":item[1]['name']}
                    implementors.append(dic)
                except:
                    pass
        name_full = self.retrieve_zip_file(month,year,"full")
        name_update = self.retrieve_zip_file(month,year,"update")
        try:
            os.remove(name_full)
            os.remove(name_update)
        except:
            pass
        return implementors


if __name__=="__main__":
    KBO=KBO()
    KBO.get_kbo_implementors(4,2024)