# Checkmk Plugin: Microsoft 365 Special Agent

## Plugin Information
The Microsoft 365 Special Agent can be integrated into Checkmk 2.3 or newer.

You can download the .mkp file from releases in this repository to upload it directly to your Checkmk site.

The Plugin provides monitoring of these components:
- Microsoft 365 Group-Based Licensing
- Microsoft 365 Licenses
- Microsoft 365 Service Health

## Prerequisites

This Special Agent uses the Microsoft Graph API to collect the monitoring data.
To access the API, you need a Microsoft Entra Tenant and a Microsoft Entra App Registration with a secret.
For a configuration guide, see the "Steps to get it working" section.

You need at least these API **application** permissions for your App Registration to use all the checks:
- *GroupMember.Read.All*
- *Organization.Read.All*
- *ServiceHealth.Read.All*

For a more granular option, the required API permissions per check are listed in the next sections.

To implement the check, you need to configure the *Microsoft 365* Special Agent in Checkmk.
You will need the Microsoft Entra Tenant ID, the Microsoft Entra App Registration ID and Secret.
When you configure the Special Agent, you have the option to select only the services that you want to monitor. You do not have to implement all the checks, but at least one of them.

## Check Details
### Microsoft 365 Group-Based Licensing

#### Description

This check monitors the Microsoft group-based licensing errors from a Microsoft 365 tenant.
It will show the count of groups with license assignment errors.

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/f8ecdd91-22e9-4768-822c-6a40a8183a78)

#### Checkmk Parameters

No parameters

#### Microsoft Graph API

**API permissions**: At  least *GroupMember.Read.All* (Application permission)

**Endpoint**: *https://graph.microsoft.com/v1.0/groups*
  
### Microsoft 365 Licenses

#### Description

This check monitors all the Microsoft 365 licenses available in your Microsoft 365 Tenant. 
Only licenses with a capabilityStatus of "warning" or "enabled" are displayed.

| State | Description |
| -------- | ------- |
| Enabled | The count of units that are currently active for the service SKU subscription. |
| lockedOut | The count of units that are inaccessible due to the customer canceling their service SKU subscription. |
| suspended | The count of units that are on hold because the service SKU subscription was canceled. These units cannot be assigned but can be reactivated before deletion. |
| warning | The count of units in a warning state. After the service SKU subscription expires, the customer has a grace period to renew before it is canceled and moved to a suspended state. |

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/72522c4c-9fa9-4a1d-bcb9-7f992b9611e2)

#### Checkmk Parameters

1. **Licenses lower levels**: Set lower-level thresholds for the number of remaining available app licenses as absolute or percentage values. To ignore the remaining available licenses, Select "Percentage" or "Absolute" and "No levels".

#### Microsoft Graph API

**API permissions**: At  least *Organization.Read.All* (Application permission)

**Endpoint**: *https://graph.microsoft.com/v1.0/subscribedSkus*
  
### Microsoft 365 Service Health

#### Description

This check monitors the service health status from a Microsoft 365 Tenant. 
Only licensed services are displayed.

The check uses the SKU name as the service name.
To find the corresponding product name, go to https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/eb7c23d1-abf4-4278-8b45-80fe2674858a)

#### Checkmk Parameters

1. **Severity level incident**: Set the severity level of the issue type incident. The default severity level is critical.
2. **Severity level advisory**: Set the severity level of the issue type advisory. The default severity level is warning.

#### Microsoft Graph API

**API permissions**: At  least *ServiceHealth.Read.All* (Application permission)

**Endpoint**: *https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/healthOverviews*
- Get all licensed services from the Microsoft 365 Tenant.

**Endpoint**: *https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/issues*
- Get all active Microsoft 365 health issues


## Steps to get it working

To use this Checkmk Special Agent, you must configure a Microsoft Entra Application to access the Microsoft Graph API endpoints.
You must also have a host in Checkmk and configure the Special Agent rule for the host.

### Microsoft Entra Configuration
#### Register an Application

1. Sign in to the Microsoft Entra Admin Center (https://entra.microsoft.com) as a Global Administrator (at least a Privileged Role Administrator)
2. Browse to **Identity** > **Applications** > **App registrations**
3. Select **New registration**
4. Provide a meaningful name (e.g. "Checkmk Special Agent")
5. Select **Accounts in this organizational directory only**
6. Do not specify a **Redirect URI**
7. Click **Register**

> [!NOTE]
> In the overview of your new application registration you will find the **Application (client) ID** and the **Directory (tenant) ID**.
> You will need this information later for the configuration of the Checkmk Special Agent.

#### Configure the Application
1. Go to **API permissions**
2. Click **Add a permission** > **Microsoft Graph** > **Application permissions**
3. Add all API permissions for all services that you want to monitor (see sections above)
4. Select **Grant admin consent** > **Yes**
5. Go to **Certificates & secrets** and click on **New client secret**
6. Insert a description (e.g. the Checkmk Site name) and select an expiration period for the secret

### Checkmk Special Agent Configuration

1. Log in to your Checkmk Site
   
#### Add a New Password

1. Browse to **Setup** > **Passwords**
2. Select **Add password**
3. Specify a **Unique ID** and a **Ttile**
4. Copy the generated secret from the Microsoft Entra Admin Center to the **Password** field
5. Click **Save**

#### Add Checkmk Host

1. Add a new host in **Setup** > **Hosts**
2. Configure your custom settings and set
 - **IP address family**: No IP
 - **Checkmk agent / API integrations**: API integrations if configured, else Checkmk agent
3. Save

#### Add Special Agent Rule

1. Navigate to the Special Agent rule **Setup** > **Microsoft 365** (use the search bar)
2. Add a new rule and configure the required settings
- **Application (client) ID** and **Directory (tenant) ID** from the Microsoft Entra Application
- For **Client secret** select **From password store** and the password from **Add a New Password**
- Select all services that you want to monitor
- Add the newly created host in **Explicit hosts**
3. Save and go to your new host and discover your new services
4. Activate the changes
