# Developing Integrations
The SecureChange Request Add-on script can be easily extended by creating additional integration scripts using Python.  This document provides details on developing new integration files to be utilized with the core script.

An integration file template can be found [here](https://raw.githubusercontent.com/jtmoran/SecureChange-Request-Addon-Script/master/Integrations/integration.py.example).  This can be used as a framework for developing your own integrations.

Previously published integrations can be found [here](https://github.com/jtmoran/SecureChange-Request-Addon-Script/tree/master/Integrations).  Exploring these previously published integrations can be helpful in getting started with your own.

## Overview

When the SecureChange Request Add-on script (**core script**) is executed by SecureChange, ticket information will be gathered to be passed to the integration file(s).  The core script will then iterate through the directory `./bin/integrations` looking for any `*.py` files, which are the **integration scripts**.  For each integration script, the core script will call the `get_data` function of the integration script and pass the ticket information as a dict object (along with the logger) to the function.  The `get_data` function may perform any action, including calling other functions or scripts, in order to enrich the ticket information.  Finally, the `get_data` function should return a formatted string with the information to be added to the SecureChange ticket as a comment.

**Note**: Only files intended to be directly executed by the SecureChange Request Add-on script should be placed in the `./bin/integrations` directory. Any dependencies should be installed in `./lib` and referenced from that directory.  

#### Input
The core script will pass two objects to the `get_data` function of the integration script:
- ticket_info [dict] - SecureChange ticket information
- logger [logging] - Logging object to write entries to the log file

`ticket_info` structure:

    {
        'Id': int (Ticket ID), 
        'Subject': str (Ticket subject), 
        'WorkflowName': str (Name of ticket workflow), 
        'Requester': str (Full name of tickter requester), 
        'RequesterId': int (System ID of ticket requetser), 
        'Status': str (Current status of ticket), 
        'Comments': str (Ticket comments), 
        'Requests': [
            {
                'Sources': [
                    {
                        'Ip': str (IPv4 address.  Ex: 192.168.1.1),
                        'Mask': str (Subnet mask.  Ex: 255.255.255.255), 
                        'Cidr': str (CIDR notation.  Ex: 32), 
                        'Private': bool (Is the IP address private?)
                    }
                ], 
                'Destinations': [
                    {
                        'Ip': str (IPv4 address.  Ex: 192.168.1.1),
                        'Mask': str (Subnet mask.  Ex: 255.255.255.255), 
                        'Cidr': str (CIDR notation.  Ex: 32), 
                        'Private': bool (Is the IP address private?)
                    }
                ], 
                'Services': [
                    {
                        'Protocol': str (TCP or UDP), 
                        'Min': str (Lowest port in range), 
                        'Max': str (Highest port in range)
                    }
                ]
            }
        ]
    }

#### Logging
Logging to the main log file can be accomplished utilizing the logger object which is passed to the `get_data` function of the integration script when the script is called.  For example:

    logging.error("This is an error message")
    logging.debug("This is a debug message")

The log level is determined by the level set in `./conf/settings.conf`.

#### Integration Configuration Parameters
Integration configuration parameters can be stored in the file `./bin/integrations/integration_config.txt`.  Add new integration  configuration parameters to the file as follows:

    [YOUR_INTEGRATION_NAME]
    YOUR_PARAMETER_1 = "YOUR VALUE 1"
    YOUR_PARAMETER_2 = "YOUR VALUE 2"
These parameters can be retrieved within your integration code as shown in the [example script](https://raw.githubusercontent.com/jtmoran/SecureChange-Ticket-Enrichment/master/Integrations/integration.py.example) as follows:

    config = configparser.ConfigParser()
    config.read_file(os.path.join(script_path, "bin/integrations/integration_config.txt"))
    param_1 = config.get('YOUR_INTEGRATION_NAME', 'YOUR_PARAMETER_1').strip('"')
    param_2 = config.get('YOUR_INTEGRATION_NAME', 'YOUR_PARAMETER_2').strip('"')

#### Output

The final enriched output which is to be added back to the SecureChange ticket should be returned by the `get_data` function as a string.  This string will be displayed in SecureChange as plain text, and can contain formatting such as multiple spaces and newlines.  

Keep in mind that only a single string may be returned to be added to SecureChange.  Results for multiple IPs or multiple data sources for a single integration should be concatenated and returned as a single string. 

If an error is encountered during the execution of the integration script and you wish to return an error message to be added to the SecureChange comments, you may return the error message as a string as you would any other results.  Note that it is not recommended to return detailed error messages to the SecureChange comments as it will clutter the view; detailed error messages should be logged using the `logging` object.

If an error is encountered during the execution of the integration script and you do not wish to return any information to the SecureChange comments, you may return `None` instead of `str`.
