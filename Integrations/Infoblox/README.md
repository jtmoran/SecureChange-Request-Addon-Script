## Infoblox
This integration queries Infoblox for any /32 IP addresses in the ticket and adds the Infoblox information to the ticket comments.

**Installer:** Infoblox.run

**Code:** Infoblox.py

### Configuration

**Header:** `[Infoblox]`

**Parameters**
| Name | Type | Description | Example |
| :-------------: | :----------: | :----------- | :----------- |
| IB_HOST | String | Infoblox IP address or FQDN | 192.168.1.1 |
| IB_USER | String | Infoblox user name | admin |
| IB_PASS | String | Infoblox password | Password1! |
| IB_APIV | String | Infoblox API version | 2.7 |

## Infoblox Type Check
This integration queries Infoblox and examines the IP Type information returned.  If the IP Type matches any of the Types specified in the integration configuration (for example, DHCP), the ticket will be rejected with the comment specified in the integration configuration.

**Installer:** Infoblox_Type_Check.run

**Code:** Infoblox_Type_Check.py

### Configuration

**Header:** `[Infoblox_Type_Check]`

**Parameters**
| Name | Type | Description | Example |
| :-------------: | :----------: | :----------- | :----------- |
| IB_HOST | String | Infoblox IP address or FQDN | 192.168.1.1 |
| IB_USER | String | Infoblox user name | admin |
| IB_PASS | String | Infoblox password | Password1! |
| IB_APIV | String | Infoblox API version | 2.7 |
| IB_TYPES | List | List of IP address types | DHCP, RESERVED_RANGE +
| IB_MESG | String | Message to be added to the rejection comments | Requests may not be submitted for dynamic (DHCP) IP addresses
