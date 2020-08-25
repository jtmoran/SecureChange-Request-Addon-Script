import os
script_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../.."))

import sys
sys.path.append(os.path.join(script_path, "lib"))
sys.path.append(os.path.join(script_path, "bin/integrations"))

import json
import configparser
import requests
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from tabulate import tabulate
from io import StringIO

requests.packages.urllib3.disable_warnings()

# './integration_config.txt' can be used to store configuration parameters for your
# integration.  The example below sets two variables based on the parameters in the
# configuration file for the example integration named 'YOUR_INTEGRATION_NAME'.

config = configparser.ConfigParser()
config.read(os.path.join(script_path, "bin/integrations/integration_config.txt"))
SP_HOST = config.get('Splunk', 'SP_HOST').strip('"')
SP_PORT = config.get('Splunk', 'SP_PORT').strip('"')
SP_PROTO = config.get('Splunk', 'SP_PROTO').strip('"')
SP_USER = config.get('Splunk', 'SP_USER').strip('"')
SP_PASS = config.get('Splunk', 'SP_PASS').strip('"')
SP_DAYS = config.get('Splunk', 'SP_DAYS').strip('"')
SP_QUERY = config.get('Splunk', 'SP_QUERY').strip('"')


# Send search query to Splunk
def search(ip, query):
    search_url = "{}://{}:{}/services/search/jobs".format(SP_PROTO, SP_HOST, SP_PORT)

    # Set headers and payload
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "output_mode": "json"
    }
    # Set search query
    search = query.replace("#IP#", ip)
    body = {
        "search": "search {}".format(search),
        "earliest_time": "-{}Days".format(SP_DAYS)
    }

    try:
        # Send query
        response = requests.post(search_url, verify=False, headers=headers, params=payload, auth=(SP_USER, SP_PASS), data=body)
        # If successful, return SID
        if response.status_code == 201:
            return (True, response.json()['sid'])
        # If not successful, return error message
        else:
            return (False, "Unable to query Splunk - Error {}: {}".format(response.status_code, response.text))

    except Exception as e:
        return (False, "Unable to query Splunk - {}".format(e))


# Check query status
def check_status(sid):
    status_url = "{}://{}:{}/services/search/jobs/{}".format(SP_PROTO, SP_HOST, SP_PORT, sid)

    # Set headers and payload
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "output_mode": "json"
    }
    try:
        # Check status
        response = requests.get(status_url, verify=False, headers=headers, params=payload, auth=(SP_USER, SP_PASS))
        # If successful, return status
        if response.status_code == 201 or response.status_code == 200:
            return (True, response.json()["entry"][0]["content"]["dispatchState"])
        # If not successful, return error message
        else:
            return (False, "Unable to query Splunk - Error {}: {}".format(response.status_code, response.text))

    except Exception as e:
        return (False, "Unable to query Splunk - {}".format(e))


# Get query results
def get_results(sid):
    result_url = "{}://{}:{}/services/search/jobs/{}/results".format(SP_PROTO, SP_HOST, SP_PORT, sid)

    # Set headers and payload
    headers = {
        "Accept": "application/text",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "output_mode": "csv"
    }
    try:
        # Get results
        response = requests.get(result_url, verify=False, headers=headers, params=payload, auth=(SP_USER, SP_PASS))
        # If successful, return retults
        if response.status_code == 201 or response.status_code == 200:
            return response.text
        # If not successful, return error message
        else:
            return (False, "Unable to query Splunk - Error {}: {}".format(response.status_code, response.text))

    except Exception as e:
        return (False, "Unable to query Splunk - {}".format(e))


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
    return_str = ""

    # Log integration starting
    logger.info("Running '{}' integration".format(__name__))

    queries = []
    try:
        for q in json.loads(SP_QUERY):
            if "name" in q.keys() and "query" in q.keys():
                if len(q["name"]) > 0 and len(q["query"]) > 0:
                    queries.append(q)
    except Exception as e:
        logger.error('Error parsing query JSON from configuration file.  SP_QUERY format should be [{"name": "<your_query_name>", "query", "<your_splunk_query>"}]')
        return None

    try:

        for req in ticket_info['Requests']:
            for src in req['Sources']:
                if src['Cidr'] == '32':
                    for q in queries:
                        sid = search(src["Ip"], q["query"])
                        status = check_status(sid[1])
                        sub_status = ""
                        while status[1] != "DONE" and sub_status == "" and status[0]:
                            if status == "PAUSED":
                                sub_status = status
                            elif status == "FAILED":
                                sub_status = status
                            else:
                                status = check_status(sid[1])
                        if sub_status != "":
                             return_str = "{}\n\nUnable to complete Splunk query '{}' for {}: {}".format(return_str, q["name"], src["Ip"], sub_status)
                        elif not status[0]:
                             return_str = "{}\n\nUnable to complete Splunk query '{}' for {}: {}".format(return_str, q["name"], src["Ip"], status[1])
                        else:
                            data = get_results(sid[1])
                            if len(data) > 0:
                                data = StringIO(get_results(sid[1]))
                                df = pd.read_csv(data, sep=",")
                                table = tabulate(df, showindex=False, headers=df.columns, tablefmt="simple")
                                table = "    ".join(table.splitlines(1))
                                return_str = "{}\n\nSplunk query '{}' results for {}:\n\n    {}".format(return_str, q["name"], src["Ip"], table)
                            else:
                                return_str = "{}\n\nSplunk query '{}' results for {}:\n\n    No results found".format(return_str, q["name"], src["Ip"])

            for dst in req['Destinations']:
                if dst['Cidr'] == '32':
                    for q in queries:
                        sid = search(dst["Ip"], q["query"])
                        status = check_status(sid[1])
                        sub_status = ""
                        while status[1] != "DONE" and sub_status == "" and status[0]:
                            if status == "PAUSED":
                                sub_status = status
                            elif status == "FAILED":
                                sub_status = status
                            else:
                                status = check_status(sid[1])
                        if sub_status != "":
                             return_str = "{}\n\nUnable to complete Splunk query '{}' for {}: {}".format(return_str, q["name"], dst["Ip"], sub_status)
                        elif not status[0]:
                             return_str = "{}\n\nUnable to complete Splunk query '{}' for {}: {}".format(return_str, q["name"], dst["Ip"], status[1])
                        else:
                            data = get_results(sid[1])
                            if len(data) > 0:
                                data = StringIO(get_results(sid[1]))
                                df = pd.read_csv(data, sep=",")
                                table = tabulate(df, showindex=False, headers=df.columns, tablefmt="simple")
                                table = "    ".join(table.splitlines(1))
                                return_str = "{}\n\nSplunk query '{}' results for {}:\n\n    {}".format(return_str, q["name"], dst["Ip"], table)
                            else:
                                return_str = "{}\n\nSplunk query '{}' results for {}:\n\n    No results found".format(return_str, q["name"], dst["Ip"])


    except Exception as e:

        # Log the error and return an empty string
        logger.error("Error: {}".format(e))
        return None

    # Log integration completing
    logger.info("{} integration completed".format(__name__))

    # Return comment
    return return_str
