# SecureChange Request Add-on Script

The SecureChange Request Add-on script can be downloaded [here](https://www.dropbox.com/s/jfefdl9n70g4h72/securechange_ticket_enrichment.run?dl=1).

The SecureChange Request Add-on script can be used to enrich or take action based on source IPs, destination IPs, and ports from Tufin SecureChange Firewall Change Request and Server Decommission tickets.  This extensible script passes ticket information in JSON format to one or more integration scripts, which can be used to enrich the ticket information using any third-party solution.  The enriched information is then returned as a formatted string, which is added as a comment to the SecureChange ticket.

![Infoblox Example](https://raw.githubusercontent.com/jtmoran/SecureChange-Request-Addon-Script/master/Screenshots/Example%20Results.PNG?raw=true)

## Installation

**NOTE**: To operate correctly, the SecureChange Request Add-on script must be installed on the SecureChange server.

To install the SecureChange Request Add-on script:

1. Download the installer [here](https://www.dropbox.com/s/jfefdl9n70g4h72/securechange_ticket_enrichment.run?dl=1)
2. Run the following commands:

    `chmod +x securechange_request_addon_script.run`
    
    `./securechange_request_addon_script.run --target <installation_directory>/securechange_request_addon_script`

The default configuration should suffice for most installations.  If you need to modify the configuration, or change the SecureChange credentials you provided during installation, please read the Configuration section.  Otherwise, you may skip to the Integration Setup section.

## Configuration

#### Setting SecureChange Credentials
During  installation, you will be prompted to enter your SecureChange credentials.  The credentials can be changed at any time by running the command:

`<install_dir>/python/bin/python3 <install_dir>/bin/set_secure_store.py -o securechange`

#### Script Settings

Script settings, such as the log location, log level, and SecureChange host are stored in `<install_dir>/conf/settings.conf`.  The default settings should be sufficient for most installations.

**IMPORTANT**, this script should only be run from the SecureChange server, so the SecureChange host should remain `127.0.0.1`.  Please contact Tufin before attempting to utilize this script from another location.

## Integration Setup

**IMPORTANT**: Only files intended to be directly executed by the SecureChange Request Add-on script should be placed in the `./bin/integrations` directory. Any dependencies should be installed in `./lib` and referenced from that directory.  

#### Installing Integrations with Installers

Many integrations are packaged as `.run` files, which will install the integration and add the appropriate lines to the configuration file automatically.

To install a new integration with an installer, download the `.run` file and execute the file with the `--target` parameter specifying the root directory of your SecureChange Request Add-on script installation.  For example `./FortiSIEM.run --target /usr/local/securechange_request_addon_script`.

If the integration fails, or no integration installer is available, you may install the integration manually as described in the next section.

Once the installation has completed, you must configuration the integration by setting the configuration parameters in `./bin/integrations/integration_config.txt`.  For more information on configuration, see the Integration Configuration section below.

#### Installing Integrations Manually

Integrations without a `.run` installer will be in the form of raw Python code and will need to be installed manually.  

The SecureChange Request Add-on script will run all `*.py` integration files located in `./bin/integrations`.  To install a new integration manually, download the `.py` file and place the integration file in this directory.  

Once the script has been installed, you must configuration the integration by setting the configuration parameters in `./bin/integrations/integration_config.txt`.  You will need to add the appropriate lines to the configuration file manually, as described in the next section.

#### Integration Configuration

Each integration receives its configuration parameters from the file `./bin/integrations/integration_config.txt`.  These configuration parameters may include an IP or FQDN, credentials, and other settings.  The configuration file follows the format:

    [IntegrationName]
    PARAM1 = ""
    PARAM2 = ""
    ....

It is important that the integration name and parameters match the documentation exactly.

When a `.run` installer is used to install an integration, the appropriate configuration lines will be automatically added to the configuration file.  Completing the setup process requires that you set the parameters for your installation in the file `./bin/integrations/integration_config.txt`.

If a `.run` installer is not used and the integration is installed manually, the configuration lines will also need to be added to the configuration file manually.  The beginning of the integration script should specify the required configuration lines as a comment at the beginning of the integration script.  For example:

    ''''
    The following configuration parameters should be added to ./bin/integrations/integration_config.txt:

    [ServiceNow]
    # ServiceNow IP or FQDN
    SN_HOST = ""
    # ServiceNow user name
    SN_USER = ""
    # ServiceNow password
    SN_PASS = ""
    ''''

Add the specified configuration lines and their appropriate values to `./bin/integrations/integration_config.txt` to configure the integration for use.

#### Developing Integrations

Information on developing your own custom integrations can be found [here](https://github.com/jtmoran/SecureChange-Request-Addon-Script/blob/master/Developing%20Integrations.md)

## SecureChange Setup

To configure SecureChange to utilize the Request Add-on script, navigate to **Settings** > **SecureChange API** and follow these steps:

1. Click **Add Script** in the bottom left corner
2. Give your script a descriptive name, such as **Request Add-on**
3. For the **Full Path**, provide the full path, including the script name, of your SecureChange Request Add-on installation.  For example `/usr/local/bin/securechange_request_addon_script/bin/request_addon.py`
4. Click **Test** to ensure SecureChange can access the script
5. Enter a descriptive **Trigger Group Name**, such as **Firewall Change Request**
6. Select **Firewall Change Request** from the **Select Workflow** dropdown, or your custom Firewall Change Request workflow
7. Select **Create** from the **Triggers** list
8. In the **Trigger Groups** area, click **Add Trigger**
9. Repeat steps 5-7 using the **Server Decommission** workflow, or your custom Server Decommission workflow
10. Click **Save**

Once completed, your configuration should be as shown below:

![SecureChange Setup](https://raw.githubusercontent.com/jtmoran/SecureChange-Request-Addon-Script/master/Screenshots/SecureChange%20Setup.PNG?raw=true)

## Troubleshooting

Logs for script and integration execution can be found in the `securechange_request_addon_script.log` file, stored in `/var/log` or the custom path set in `./conf/settings.conf`.

SecureChange error messages can be found by navigating to **Settings** > **Message Board**.

Contact Tufin support at <support@tufin.com> or through the [Tufin Portal](https://portal.tufin.com/).

