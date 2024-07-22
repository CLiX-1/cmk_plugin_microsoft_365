# Checkmk Plugin: Microsoft 365 Special Agent

## Plugin Information
The Microsoft 365 Special Agent can be integrated into Checkmk 2.3 or newer.

You can download the .mkp file from releases in this repository to upload it directly to your Checkmk site.

The Plugin provides monitoring of these components:
- Microsoft 365 Licenses
- Microsoft 365 Service Health

## Prerequisites

This Special Agent uses the Microsoft Graph API to collect the monitoring data.
To access the API, you need a Microsoft Entra Tenant and a Microsoft Entra App Registration with a secret.

You need at least these API **application** permissions for your App Registration:
- *Organization.Read.All*
- *ServiceHealth.Read.All*

For a more granular option, the required API permissions per check are listed in the next sections.

To implement the check, you need to configure the *Microsoft 365* Special Agent in Checkmk.
You will need the Microsoft Entra Tenant ID, the Microsoft Entra App Registration ID and Secret.
When you configure the Special Agent, you have the option to select only the services that you want to monitor. You do not have to implement all the checks, but at least one of them.

## Microsoft 365 Licenses

### Description

This check monitors all the Microsoft 365 licenses available in your Microsoft 365 Tenant. 
Only licenses with a capabilityStatus of "warning" or "enabled" are displayed.

| State | Description |
| -------- | ------- |
| Enabled | The count of units that are currently active for the service SKU subscription. |
| lockedOut | The count of units that are inaccessible due to the customer canceling their service SKU subscription. |
| suspended | The count of units that are on hold because the service SKU subscription was canceled. These units cannot be assigned but can be reactivated before deletion. |
| warning | The count of units in a warning state. After the service SKU subscription expires, the customer has a grace period to renew before it is canceled and moved to a suspended state. |

### Checkmk service example

![grafik](https://github.com/user-attachments/assets/72522c4c-9fa9-4a1d-bcb9-7f992b9611e2)

### Checkmk Parameters

1. **Licenses lower levels**: Set lower-level thresholds for the number of remaining available app licenses as absolute or percentage values. To ignore the remaining available licenses, Select "Percentage" or "Absolute" and "No levels".

### Microsoft Graph API

**API permissions**: At  least *Organization.Read.All* (Application permission)

**Endpoint**: *https://graph.microsoft.com/v1.0/subscribedSkus*

## Microsoft 365 Service Health

### Description

This check monitors the service health status from a Microsoft 365 Tenant. 
Only licensed services are displayed.

The check uses the SKU name as the service name.
To find the corresponding product name, go to https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference

### Checkmk service example

![grafik](https://github.com/user-attachments/assets/eb7c23d1-abf4-4278-8b45-80fe2674858a)

### Checkmk Parameters

1. **Severity level incident**: Set the severity level of the issue type incident. The default severity level is critical.
2. **Severity level advisory**: Set the severity level of the issue type advisory. The default severity level is warning.

### Microsoft Graph API

**API permissions**: At  least *ServiceHealth.Read.All* (Application permission)

**Endpoint**: *https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/healthOverviews*
- Get all licensed services from the Microsoft 365 Tenant.

**Endpoint**: *https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/issues*
- Get all active Microsoft 365 health issues
