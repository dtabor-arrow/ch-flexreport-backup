import os
import json
import requests
import csv

# Prompt the user for the API key
api_key = input("Enter your CloudHealth API key: ")

# Define the GraphQL query
graphql_query = {
    "query": "mutation Login($apiKey: String!) { loginAPI(apiKey: $apiKey) { accessToken } }",
    "variables": {
        "apiKey": api_key
    }
}

# Make the login request and extract the access token
response = requests.post('https://apps.cloudhealthtech.com/graphql', json=graphql_query)
response.raise_for_status()
data = response.json()
ACCESSTOKEN = data['data']['loginAPI']['accessToken']

# Define the GraphQL query to get available datasets
datasets_query = {
    "query": "query queryReq { dataSources { datasetName } }",
    "variables": {}
}

# Make the request to get available datasets
headers = {
    "Authorization": f"Bearer {ACCESSTOKEN}",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "application/json",
    "Connection": "keep-alive"
}
response = requests.post('https://apps.cloudhealthtech.com/graphql', json=datasets_query, headers=headers)
response.raise_for_status()
data = response.json()
datasets = data['data']['dataSources']

# Create a list to store report data
report_data_list = []

# Fetch and store report data in the list
for dataset in datasets:
    dataset_name = dataset['datasetName']
    
    # Define the GraphQL query to get FlexReports for the current dataset
    reports_query = {
        "query": f'query queryReports{dataset_name} {{ flexReports(dataset: "{dataset_name}") {{ id name description createdBy lastUpdatedOn }} }}',
        "variables": {}
    }
    
    # Make the request to get FlexReports for the current dataset
    response = requests.post('https://apps.cloudhealthtech.com/graphql', json=reports_query, headers=headers)
    response.raise_for_status()
    report_data = response.json()
    report_list = report_data['data']['flexReports']
    
    # Append report data to the list, including the dataset name
    for report in report_list:
        report_data_list.append({"name": report['name'], "id": report['id'], "createdBy": report['createdBy'], "dataset_name": dataset_name})

# Sort the report data list alphabetically by the lowercase 'name' column (case-insensitive)
report_data_list.sort(key=lambda x: x['name'].lower())

# Write the sorted report data to the CSV file
with open('report-list.csv', 'w', newline='') as csv_file:
    fieldnames = ["name", "id", "createdBy", "dataset_name"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#    writer.writeheader()
    
    for report_data in report_data_list:
        writer.writerow(report_data)

print("Getting all saved FlexReports for all datasets, saving them to report-list.csv")
