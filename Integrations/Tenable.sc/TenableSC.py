'''
The following configuration parameters should be added to ./bin/integrations/integration_config.txt:
[Tenable_SC]
# IP or FQDN for Tenable
TSC_HOST = ""
# Tenable user name
TSC_USER = ""
# Tenable password
TSC_PASS = ""
'''

import os
script_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../.."))

import sys
sys.path.append(os.path.join(script_path, "lib"))
sys.path.append(os.path.join(script_path, "bin/integrations"))

import configparser
import requests
import json

requests.packages.urllib3.disable_warnings()

# './integration_config.txt' can be used to store configuration parameters for your
# integration.  The example below sets two variables based on the parameters in the
# configuration file for the example integration named 'YOUR_INTEGRATION_NAME'.

config = configparser.ConfigParser()
config.read(os.path.join(script_path, "bin/integrations/integration_config.txt"))
TSC_HOST = config.get('Tenable_SC', 'TSC_HOST').strip('"')
TSC_USER = config.get('Tenable_SC', 'TSC_USER').strip('"')
TSC_PASS = config.get('Tenable_SC', 'TSC_PASS').strip('"')


# Query for vulnerabilities mathcing ip
def ip_query(session, token, ip, logger):
    result = ""
    try:
        headers = {
            'X-SecurityCenter': token,
            'Content-type': 'application/json'
        }
        payload = {
            "type" : "vuln",
            "query" : {
                "tool": "sumid",
                "filters" : [
                    {
                        "filterName": "ip",
                        "value": ip,
                        "operator": "="
                    },
                    {
                        "filterName": "severity",
                        "value": "0",
                        "operator": "!="
                    }
                ],
                "sortField": "severity",
                "sortDir": "DESC",
                "type": "vuln"
            },
            "sourceType" : "cumulative"
        }
        vuln_url =  "https://{}/rest/analysis".format(TSC_HOST)
        vuln_response = session.post(vuln_url, headers=headers, data=json.dumps(payload), verify=False)
        # If a 200 status code was not returned, return error
        if vuln_response.status_code != 200:
            error = "Unable to query Tenable for {}: {} - {}".format(ip, vuln_response.status_code, vuln_response.text)
            result = error
            logger.error(error)
            return result
        # Response received
        else:
            vuln_json = vuln_response.json()["response"]
            # If no records were found, return
            if int(vuln_json["totalRecords"]) < 1:
                result = "No Tenable.sc results found for {}".format(ip)
                return result
            vuln_info = ""
            for vuln in vuln_json["results"]:
                temp_vuln = "    Name:      {}\n    Family:    {}\n    Plugin ID: {}\n    Severity:  {}\n    VPR Score: {}".format(vuln["name"], vuln["family"]["name"], vuln["pluginID"], vuln["severity"]["name"], vuln["vprScore"])
                vuln_info = "{}\n\n{}".format(vuln_info, temp_vuln)
            result = vuln_info.strip()
            return result

    except Exception as e:
        error = "Unable to query Tenable for {}: {}".format(ip, e)
        result = error
        logger.error(error)
        return result


# Query for vulnerabilities mathcing ip and port
def ip_port_query(session, token, ip, port, logger):
    result = ""
    try:
        headers = {
            'X-SecurityCenter': token,
            'Content-type': 'application/json'
        }

        payload = {
            "type" : "vuln",
            "query" : {
                "tool": "sumid",
                "filters" : [
                    {
                        "filterName": "ip",
                        "value": ip,
                        "operator": "="
                    },
                    {
                        "filterName": "port",
                        "value": port,
                        "operator": "="
                    },
                    {
                        "filterName": "severity",
                        "value": "0",
                        "operator": "!="
                    }
                ],
                "sortField": "severity",
                "sortDir": "DESC",
                "type": "vuln"
            },
            "sourceType" : "cumulative"
        }

        vuln_url =  "https://{}/rest/analysis".format(TSC_HOST)
        vuln_response = session.post(vuln_url, headers=headers, data=json.dumps(payload), verify=False)
        # If a 200 status code was not returned, return error
        if vuln_response.status_code != 200:
            error = "Unable to query Tenable for {}: {} - {}".format(ip, vuln_response.status_code, vuln_response.text)
            result = error
            logger.error(error)
            return result
        # Response received
        else:
            vuln_json = vuln_response.json()["response"]
            # If no records were found, return
            if int(vuln_json["totalRecords"]) < 1:
                result = "No Tenable.sc results found for {}:{}".format(ip, port)
                return result
            vuln_info = ""
            for vuln in vuln_json["results"]:
                temp_vuln = "    Name:      {}\n    Family:    {}\n    Plugin ID: {}\n    Severity:  {}\n    VPR Score: {}".format(vuln["name"], vuln["family"]["name"], vuln["pluginID"], vuln["severity"]["name"], vuln["vprScore"])
                vuln_info = "{}\n\n{}".format(vuln_info, temp_vuln)
            result = vuln_info.strip()
            return result

    except Exception as e:
        error = "Unable to query Tenable for {}: {}".format(ip, e)
        result = error
        logger.error(error)
        return result


# Get Tenable token
def get_token(session, logger):
    payload = {
        'username': TSC_USER,
        'password': TSC_PASS,
        'releaseSession': 'false'
    }
    token_url = "https://{}/rest/token".format(TSC_HOST)
    try:
        # Send token request
        response = session.post(token_url, data=json.dumps(payload), verify=False)
        # 403 indicates a problem with authentication, return error
        if response.status_code == 403:
            error = "Unable to authenicate to Tenable: {}".format(response.json()["error_msg"])
            logger.error(error)
            exit(-1)
        # If a 200 status code was not returned, return error
        elif response.status_code != 200:
            error = "Unable to authenicate to Tenable: {} - {}".format(response.status_code, response.text)
            logger.error(error)
            exit(-1)
        # Response received
        else:
            token_json = response.json()
            # If a token was not returned, return an error
            if "token" not in token_json["response"]:
                error = "Unable to authenicate to Tenable: No authentication returned"
                logger.error(error)
                exit(-1)
            # Return token
            return str(token_json['response']['token'])
    except Exception as e:
        error = "Unable to authenicate to Tenable: {}".format(e)
        logger.error(error)
        exit(-1)


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

    try:
        session = requests.Session()
        token = get_token(session, logger)
        no_results = ""
        # For each request in the ticket
        for req in ticket_info['Requests']:
            # For each source in reuest
            for src in req['Sources']:
                # If the source is a /32 IP
                if src['Cidr'] == '32':
                    # Get vulnerability results
                    tmp_result = ip_query(session, token, src["Ip"], logger)
                    # If vulnerabilities were found, add them to the results
                    if len(tmp_result.split('\n')) > 2:
                        return_str = '{}\n\nTenable.sc results for Source {} :\n\n    {}'.format(return_str, src["Ip"], tmp_result)
                    # If no vulnerabilities were found, add it to the no results list
                    else:
                        no_results = "{}\n{}".format(no_results, tmp_result)
            # For each destination in reuest
            for dst in req['Destinations']:
                # If the destination is a /32 IP
                if dst['Cidr'] == '32':
                    # For each service in the request
                    for svc in req['Services']:
                        # If the service is ALL, query just the IP
                        if svc['Min'] == "0" and svc['Max'] == "65536":
                            tmp_result = ip_query(session, token, dst["Ip"], logger)
                            # If vulnerabilities were found, add them to the results
                            if len(tmp_result.split('\n')) > 2:
                                return_str = '{}\n\nTenable.sc results for Destination {} (ALL):\n\n    {}'.format(return_str, dst["Ip"], tmp_result)
                            # If no vulnerabilities were found, add it to the no results list
                            else:
                                no_results = "{}\n{}".format(no_results, tmp_result)
                        # If the service is NOT all, query the IP and port combinations
                        else:
                            for port in range(int(svc['Min']), int(svc['Max']) + 1):
                                tmp_result = ip_port_query(session, token, dst["Ip"], port, logger)
                                # If vulnerabilities were found, add them to the results
                                if len(tmp_result.split('\n')) > 2:
                                    return_str = '{}\n\nTenable.sc results for Destination {}:{} :\n\n    {}'.format(return_str, dst["Ip"], port, tmp_result)
                                # If no vulnerabilities were found, add it to the no results list
                                else:
                                    no_results = "{}\n{}".format(no_results, tmp_result)
        return_str = "{}\n{}".format(return_str, no_results)
    except Exception as e:
        # Log the error and return an empty string
        logger.error("Error: {}".format(e))
        return None

    # Log integration completing
    logger.info("{} integration completed".format(__name__))

    # Return comment
    return return_str
