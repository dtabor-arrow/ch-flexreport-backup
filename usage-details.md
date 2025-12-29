# FlexReport Backup Usage Details

The FlexReport backup script performs a simple API query to download the individual JSON files for all available FlexReports.  FlexReports are defined by the JSON files and contain all of the information about the report, including the SQL statement.

The SQL statement is exactly what you would see when editing a FlexReport in CloudHealth.  With the downloaded JSON, you can simply copy/paste the SQL back in to CloudHealth to restore/recreate the original report.

## Example JSON

This is an example of a report that has been extracted from a backup .zip file

``` json
{
  "data": {
    "node": {
      "id": "crn:63253:flexreports/61a90d55-4396-47e7-a2b6-52824adc1767",
      "name": "[CHPS] AWS YTD Spend",
      "createdBy": "Dean Tabor",
      "result": {
        "reportUpdatedOn": "2025-08-14T14:49:55Z"
      },
      "query": {
        "sqlStatement": " SELECT DATE( FROM_ISO8601_TIMESTAMP (bill_BillingPeriodStartDate) ) AS BillingPeriodStartDate, product_ProductName AS ProductName, lineItem_UsageType AS usageType, SUM(lineItem_UnblendedCost) AS Cost FROM AWS_CUR WHERE split_part ( CAST( DATE( FROM_ISO8601_TIMESTAMP (bill_BillingPeriodStartDate) ) AS VARCHAR ), '-', 1 ) = split_part (CAST(current_date AS VARCHAR), '-', 1) GROUP BY DATE( FROM_ISO8601_TIMESTAMP (bill_BillingPeriodStartDate) ), product_ProductName, lineItem_UsageType ORDER BY BillingPeriodStartDate ASC; ",
        "dataset": "AWS_CUR",
        "dataGranularity": "MONTHLY",
        "needBackLinkingForTags": true,
        "limit": -1,
        "timeRange": {
          "last": 12,
          "from": null,
          "to": null,
          "excludeCurrent": null
        }
      }
    }
  }
}
```

The ```query``` section contains the full SQL and other FlexReport-related information.  You can simply copy/paste the relevant bits back in to the FlexReport editor.
