## Infoblox
This integration queries Infoblox for any /32 IP addresses in the ticket and adds the Infoblox information to the ticket comments.

## Infoblox Type Check
This integration queries Infoblox and examines the IP Type information returned.  If the IP Type matches any of the Types specified in the integration configuration (for example, DHCP), the ticket will be rejected with the comment specified in the integration configuration.
