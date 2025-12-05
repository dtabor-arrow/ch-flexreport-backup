import json
import requests
import sys

# Prompt the user for the API key
api_key = input("Enter your CloudHealth API key: ")

# Define the GraphQL query
graphql_query = {
    "query": "mutation Login($apiKey: String!) { loginAPI(apiKey: $apiKey) { accessToken } }",
    "variables": {
        "apiKey": api_key
    }
}

# GraphQL query to create the FlexReport (variables will be populated dynamically)
flex_report_query = """mutation CreateFlexReport($name: String!,$description: String!,$sqlStatement: String!,$needBackLinkingForTags: Boolean!,$dataGranularity: FlexReportDataGranularity!,$limit: Int!,$timeRangeLast: Int!) {createFlexReport(input: {name: $name,description: $description,notification: {sendUserEmail: false},query: {sqlStatement: $sqlStatement,needBackLinkingForTags: $needBackLinkingForTags,dataGranularity: $dataGranularity,limit: $limit,timeRange: {last: $timeRangeLast}}}) {id,name}}"""

# GraphQL endpoint URL
graphql_endpoint = 'https://apps.cloudhealthtech.com/graphql'

# Function to prompt the user for the filename if not provided as a parameter
def get_filename():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return input("Enter the JSON filename: ")

# Get the JSON filename
json_filename = get_filename()

# Read the FlexReport variables from the specified JSON file
try:
    with open(json_filename, "r") as json_file:
        report_definition = json.load(json_file)
except FileNotFoundError:
    print("File not found:", json_filename)
    sys.exit(1)
except Exception as e:
    print("Error reading JSON file:", str(e))
    sys.exit(1)

# Extract the relevant data from the JSON file
original_report_name = report_definition["data"]["node"]["name"]
data_granularity = report_definition["data"]["node"]["query"]["dataGranularity"]

# Append "RESTORED FROM BACKUP" to the original report name
restored_report_name = original_report_name + " RESTORED FROM BACKUP"

flex_report_variables = {
    "name": restored_report_name,
    "description": original_report_name,
    "sqlStatement": report_definition["data"]["node"]["query"]["sqlStatement"],
    "needBackLinkingForTags": report_definition["data"]["node"]["query"]["needBackLinkingForTags"],
    "dataGranularity": data_granularity,  # No quotes around data_granularity
    "limit": report_definition["data"]["node"]["query"]["limit"],
    "timeRangeLast": report_definition["data"]["node"]["query"]["timeRange"]["last"]
}

# Set the headers for the GraphQL requests
headers = {
    "Content-Type": "application/json"
}

# Make the first GraphQL API call to get the access token
access_token_response = requests.post(graphql_endpoint, json={"query": graphql_query, "variables": {"apiKey": api_key}}, headers=headers)

# Check if the request was successful
if access_token_response.status_code == 200:
    access_token_result = access_token_response.json()
    access_token = access_token_result["data"]["loginAPI"]["accessToken"]

    # Print the full GraphQL request for debugging
    print("Full GraphQL Request:")
    print(json.dumps({"query": flex_report_query, "variables": flex_report_variables}, indent=2))

    # Make the second GraphQL API call to create the FlexReport using the obtained access token
    flex_report_response = requests.post(graphql_endpoint, json={"query": flex_report_query, "variables": flex_report_variables}, headers={"Content-Type": "application/json", "Authorization": "Bearer " + access_token})

    # Print the full GraphQL response for debugging
    print("Full GraphQL Response:")
    print(json.dumps(flex_report_response.json(), indent=2))

    # Check if the FlexReport creation request was successful
    if flex_report_response.status_code == 200:
        flex_report_result = flex_report_response.json()
        flex_report_id = flex_report_result["data"]["createFlexReport"]["id"]
        print("FlexReport created successfully!")
        print("FlexReport ID:", flex_report_id)
    else:
        print("Failed to create FlexReport. Status code:", flex_report_response.status_code)
        print("Response:", flex_report_response.text)
else:
    print("Failed to retrieve access token. Status code:", access_token_response.status_code)
    print("Response:", access_token_response.text)
