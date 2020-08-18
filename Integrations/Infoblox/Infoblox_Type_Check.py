
''''
The following configuration parameters should be added to ./bin/integrations/integration_config.txt:
[Infoblox]
# Infoblox IP or FQDN
IB_HOST = ""
# Infoblox user name
IB_USER = ""
# Infoblox password
IB_PASS = ""
# Infoblox API version number, for example: 2.7
IB_APIV = ""
# List of Type values to match, for example: "DHCP, RESERVED_RANGE"
IB_TYPES = ""
# Message to be added to IP address matches, for example: "Tickets cannot be submitted for dynamic (DHCP) addresses.  Please modify your request and resubmit"
IB_MESG = ""

Example Output:

   Ticket Comments:
   
       Infoblox type check results:
       
       *** The following problems were detected:
       
       192.168.1.1 matches the address type 'RESERVED_RANGE'
       192.168.2.1 matches the address type 'RESERVED_RANGE'
       
       The ticket was REJECTED ***
       
       Full results:
       
           172.16.0.1 is okay
           192.168.1.1 matches the address type 'RESERVED_RANGE'
           No information found for 10.0.0.1
           192.168.2.1 matches the address type 'RESERVED_RANGE'",
   
   Ticket Rejection Comment:
   
       192.168.1.1 matches the address type 'RESERVED_RANGE' - Tickets cannot be submitted for dynamic (DHCP) addresses.  Please modify your request and resubmit
       192.168.2.1 matches the address type 'RESERVED_RANGE' - Tickets cannot be submitted for dynamic (DHCP) addresses.  Please modify your request and resubmit
''''

import os
script_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../.."))

import sys
sys.path.append(os.path.join(script_path, "lib"))
sys.path.append(os.path.join(script_path, "bin/integrations"))

import configparser
import requests
from common.secret_store import SecretDb
from pytos2.securechange import ScwAPI

requests.packages.urllib3.disable_warnings()

# './integration_config.txt' can be used to store configuration parameters for your
# integration.  The example below sets two variables based on the parameters in the
# configuration file for the example integration named 'YOUR_INTEGRATION_NAME'.

config = configparser.ConfigParser()
config.read(os.path.join(script_path, "bin/integrations/integration_config.txt"))
IB_HOST = config.get('Infoblox_Type_Check', 'IB_HOST').strip('"')
IB_USER = config.get('Infoblox_Type_Check', 'IB_USER').strip('"')
IB_PASS = config.get('Infoblox_Type_Check', 'IB_PASS').strip('"')
IB_APIV = config.get('Infoblox_Type_Check', 'IB_APIV').strip('"')
IB_TYPE = config.get('Infoblox_Type_Check', 'IB_TYPES').strip('"')
IB_MESG = config.get('Infoblox_Type_Check', 'IB_MESG').strip('"')
TYPE_LIST = [t.strip() for t in IB_TYPE.split(",")]


# Reject a SecureChange ticket
def reject_ticket(ticket_id, reason, logger):
    secret_helper = SecretDb()
    sc_conf = configparser.ConfigParser()
    sc_conf.read(os.path.join(script_path, "conf/settings.conf"))
    sc_host = sc_conf.get("securechange", "host")
    sc_cred = (secret_helper.get_username('securechange'), secret_helper.get_password('securechange'))
    sc_user = sc_cred[0]
    sc_pass = sc_cred[1]

    try:
        scw_api = ScwAPI(sc_host, sc_user, sc_pass)
        # Reject the ticket
        reject = scw_api.reject_ticket(ticket_id, comment=reason)
        # If the rejection was successful
        if reject.status_code == 200:
            logger.info("Ticket {} rejected with the following comment: {}".format(ticket_id, reason))
        # If the rejection was not successful
        else:
            logger.error("Error - unable to update ticket {}: Error {}".format(ticket_id, reject.status_code))
        # Return the status code
        return reject.status_code
    except Exception as e:
        logger.error("Error - unable to update ticket {}.  Error details: {}".format(ticket_id, e))
        return None


def search_ip(ip, logger):
    # Default response
    result = {"match": False, "text": "{} is okay".format(ip)}

    # Get IP address information
    ip_url = "https://{}/wapi/v{}/ipv4address?ip_address={}".format(IB_HOST, IB_APIV, ip)
    try:
        res = requests.get(ip_url, auth=(IB_USER, IB_PASS), verify=False)
        # If the request was successful
        if res.status_code == 200:
            # Try parsing the data as JSON.  If it cannot be parsed, return an error
            try:
                res.json()
            except:
                logger.error("Recieved data in invalid format: {}".format(res.text))
                result["text"] = "Invalid response recieved for {}".format(ip)

            # For each item in the response
            for item in res.json():
                # If there is a 'types' key
                if "types" in item:
                    # and the 'types' key has a value
                    if len(item["types"]) > 0:
                        # For each type
                        for type in item["types"]:
                            # If the type is in the list of types to match
                            if type in TYPE_LIST:
                                # Add a match to the result
                                result["match"] = True
                                result["text"] = "{} matches the address type '{}'".format(ip, type)
        # A 400 error indicates no results were found
        elif res.status_code == 400:
            result["text"] = "No information found for {}".format(ip)
        # If not 200 or 400, return an error
        else:
            result["text"] = "Error querying {}: ({}) {}".format(ip, res.status_code, res.reason)
    except Exception as e:
        logger.error("Error: {}".format(e))
        result["text"] = "Error querying {}: {}".format(ip, e)

    return result


def get_data(ticket_info, logger):
    """ This fucntion accepts the SecureChange access request and will return a string which
    will be added to the SecureChange ticket as a comment.  If an error occurs, return None
    and log the error via the logger.

    :param ticket_info: SecureChange ticket information
    :type ticket_info: dict
    :param logger: Tufin logger
    :type logger: pytos.common.logging.logger
    :return: Comment to be added to SecureChange ticket, or None on error
    :rtype: str | None
    """

    # This string will be returned and added as a comment to the SecureChange ticket
    return_str = "Infoblox type check results:\n"

    # Log integration starting
    logger.info("Running '{}' integration".format(__name__))

    # List of dicts with IP address restuls
    result_list = []

    try:
        # For each request -> for each source and destination
        for req in ticket_info['Requests']:
            for src in req['Sources']:
                if src['Cidr'] == '32':
                    result_list.append(search_ip(src["Ip"], logger))
            for dst in req['Destinations']:
                if dst['Cidr'] == '32':
                    result_list.append(search_ip(dst["Ip"], logger))

        temp_str = ""
        match_str = ""
        mesg_str = ""

        # Iterate through the result list
        for r in result_list:
            temp_str = "{}\n    {}".format(temp_str, r["text"])
            # If the result was a match
            if r["match"]:
                # Add result to the short and verbose strings
                match_str = "{}\n{}".format(match_str, r["text"])
                mesg_str = "{}\n{} - {}\n".format(mesg_str, r["text"], IB_MESG)
        match_str = match_str.strip()
        mesg_str = mesg_str.strip()

        # If any IP addresses resulted in a match, reject ticket and return information
        if len(match_str) > 0:
            # Reject the ticket
            reject = reject_ticket(ticket_info["Id"], mesg_str, logger)
            # If the rejection was successful, return a success message
            if reject == 200:
                return_str = "{}\n*** The following problems were detected:\n\n{}\n\nThe ticket was REJECTED ***\n\nFull results:\n{}".format(return_str, match_str, temp_str)
            # If the rejection was not successful, return an errror message
            else:
                return_str = "{}\n*** The following problems were detected:\n\n{}\n\nThere was an ERROR rejecting the ticket\nSee log for more details ***\n\nFull results:\n{}".format(return_str, match_str, temp_str)
        # If there were no matches, return information
        else:
            return_str = "{}{}".format(return_str, temp_str)

    except Exception as e:

        # Log the error and return an empty string
        logger.error("Error: {}".format(e))
        return None

    # Log integration completing
    logger.info("{} integration completed".format(__name__))

    # Return comment
    return return_str
