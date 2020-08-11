# SecureChange Ticket Enrichment Script

The SecureChange Ticket Enrichment Script can be used to enrich sources, destinations, and ports from Tufin SecureChange Firewall Change Request and Server Decommission tickets.  This extensible script passes ticket information in JSON format to one or more integration scripts, which can be used to enrich the ticket information using any third-party solution.  The enriched information is then returned as a formatted string, which is added as a comment to the SecureChange ticket.

## Script Setup

#### Set SecureChange Credentials
SecureChange credentials can be securely stored using the `set_secure_store.py` script in the `bin` directory.  Use the following command to store your credentials:

`<install_dir>/python/bin/python3 <install_dir>/bin/set_secure_store.py -o securechange`

Enter your SecureChange user name and password.  The credentials can be changed at any time by running the same command.

#### Script Settings

Script settings, such as the log location, log level, and SecureChange host are stored in `<install_dir>/conf/settings.conf`.  The default settings should be sufficient for most installations.

**Remeber**, this script should only be run from the SecureChange server, so the SecureChange host should remain `127.0.0.1`.  Please contact Tufin before attempting to utilize this script from another location.

## Integration Setup

#### Installing Integrations

The SecureChange Ticket Enrichment script will run all `*.py` integration files located in `./bin/integrations` on each execution.  To install a new integration manually, simply place the integration file in this directory.  

**Note**: Only files intended to be directly executed by the SecureChange Ticket Enrichment script should be placed in the `./bin/integrations` directory. Any dependencies should be installed in `./lib` and referenced from that directory.  

Integrations provided as packages can be installed by running the installer and providing your SecureChange Ticket Enrichment installation root directory.

#### Developing Integrations

Information on developing your own custom integrations can be found [here](https://github.com/jtmoran/SecureChange-Ticket-Enrichment/blob/master/Developing%20Integrations.md)

## SecureChange Setup

To configure SecureChange to utilize the Ticket Enrichment script, navigate to **Settings** > **SecureChange API** and follow these steps:

1. Click **Add Script** in the bottom left corner
2. Give your script a descriptive name, such as **Ticket Enrichment**
3. For the **Full Path**, provide the full path, including the script name, of your SecureChange Ticket Enrichment installation.  For example `/usr/local/bin/securechange_ticket_enrichment/bin/ticket_enrichment.py`
4. Click **Test** to ensure SecureChange can access the script
5. Enter a descriptive **Trigger Group Name**, such as **Firewall Change Request**
6. Select **Firewall Change Request** from the **Select Workflow** dropdown, or your custom Firewall Change Request workflow
7. Select **Create** from the **Triggers** list
8. In the **Trigger Groups** area, click **Add Trigger**
9. Repeat steps 5-7 using the **Server Decommission** workflow, or your custom Server Decommission workflow
10. Click **Save**

Once completed, your configuration should be as shown below:

![SecureChange Setup](https://raw.githubusercontent.com/jtmoran/SecureChange-Ticket-Enrichment/master/screenshots/SecureChange%20Setup.PNG?raw=true)

## Troubleshooting

Logs for script and integration execution can be found in the `ticket_enrichment.log` file, stored in `/var/log` or the custom path set in `./conf/settings.conf`.

SecureChange error messages can be found by navigating to **Settings** > **Message Board**.

Contact Tufin support at <support@tufin.com> or through the [Tufin Portal](https://portal.tufin.com/).

## License
©2020 [Tufin Software North America, Inc.](https://www.tufin.com)
