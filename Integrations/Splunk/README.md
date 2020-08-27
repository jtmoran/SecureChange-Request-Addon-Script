## Splunk
This integration queries Splunk using the queries specified in the integration configuration with any /32 IP addresses in the ticket and adds the search results to the ticket comments.

**Note**: To add the IP address from the SecureChange ticket to the query, add the string `#IP` to the query in the appropriate location.  At runtime, the `#IP#` variable will be replaced with the IP addresses from the ticket.

**Installer:** Splunk.run

**Code:** Splunk.py

### Requirements

This integration requires the following Python libraries:

- pandas
- tabulate

These libraries will be automatically installed when using the Splunk.run installer.  If the integration is installed manually, these libraries must also be installed manually using pip.

### Configuration

**Header:** `[Splunk]`

**Parameters**
| Name | Type | Description | Example |
| :-------------: | :----------: | :----------- | :----------- |
| SP_HOST | String | Splunk IP address or FQDN | 192.168.1.1 |
| SP_PORT | String | Splunk port (Default: 8089) | 8089 |
| SP_PROTO | String | HTTP protocol (Options: "http" or "https" (Default)) | https |
| SP_USER | String | Splunk user name | admin |
| SP_PASS | String | Splunk password | Password1! |
| SP_DAYS | String | Number of days to query Splunk logs (Default: 14) | 14 |
| SP_QUERY | String | JSON list of Splunk queries to run | See below |

**Building Queries**
The SP_QUERY configuration parameter should contain a list of one or more queries to send to Splunk in the following format:

    [{"name": "<your_query_name>", "query", "<your_splunk_query_with_#IP#>"}]

Where:

    name = The name of the query which will be displayed in the SecureChange output
    query = The Splunk query to run

The variable `#IP#` should be used in the query string to indicate where the IP address from the SecureChange ticket should be added.  For example:

    src_ip=#IP#

Any quotes in the query string should be escaped with a backslash.  For example:

    "index="_internal""

Should be written as:

    "index=\"_internal\""
    
Since comment space is limited, it is recommended results from Splunk be truncated and written to a table with only the most important columns.  This can be accomplished as follows:

    <your_search_query> | stats count by uri_path | eval uri_path = if (len(uri_path) > 30, substr(uri_path, 1, 27) + \"...\", uri_path) | table uri_path, count
    
This example will generate a table showing the count of `uri_path`, and `uri_path`  will be truncated if it is over 30 characters in length.

A full query may look as follows:

    index=\"_internal\" #IP# | stats count by uri_path | eval uri_path = if (len(uri_path) > 30, substr(uri_path, 1, 27) + \"...\", uri_path) | table uri_path, count
    
It is a good idea to build and test your queries in the Splunk UI, then add them to the SP_QUERY parameter once they are working.

### Output

    Splunk query 'Endpoint Alerts' results for 172.20.0.30 for the past 14 days:

        uri_path                          count
        ------------------------------  -------
        Win32/NetTool.Ncat.A                  6

    Splunk query 'IDS Alerts' results for 172.20.0.30 for the past 14 days:

        uri_path                          count
        ------------------------------  -------
        SSH brute force login attempt         3
        Ping with TTL=100                     1

### Versions
- 08-26-2020 - Initial upload
