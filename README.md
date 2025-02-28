# Checkmk Plugin: Microsoft 365 Special Agent

The **Microsoft 365** Special Agent is an extension for the monitoring software **Checkmk**.  
It can be integrated into Checkmk 2.3 or newer.

You can download the extension package as an `.mkp` file from the [releases](../../releases) in this repository and upload it directly to your Checkmk site.  
See the Checkmk [documentation](https://docs.checkmk.com/latest/en/mkps.html) for details.

## Plugin Information

The Plugin provides monitoring for the following components:
- Microsoft 365 Group-Based Licensing
- Microsoft 365 Licenses
- Microsoft 365 Service Health

See [Check Details](#check-details) for more information.

## Prerequisites

This Special Agent uses the Microsoft Graph API to collect the monitoring data.  
To access the API, you need a Microsoft Entra tenant and a Microsoft Entra app registration with a client secret ([Steps to Get It Working](#steps-to-get-it-working)).

You need at least the following API **application** permissions for your app registration to use all the checks:
- *GroupMember.Read.All*
- *Organization.Read.All*
- *ServiceHealth.Read.All*

For a more granular options, the required API permissions per check are listed in the next sections.

To activate the checks, you must configure the **Microsoft 365** Special Agent in Checkmk.
You will need the Microsoft Entra tenant ID, the App ID and the client secret from the Microsoft Entra app registration.
When you configure the Special Agent, you have the option to select only the services that you want to monitor. You do not have to implement all the checks, but at least one of them.

> [!NOTE]
> This plugin uses HTTPS connections to Microsoft.
>Make sure you have enabled **Trust system-wide configured CAs** or uploaded the CA certificates for the Microsoft domains in Checkmk.
>You can find these options in **Setup** > **Global settings** > **Trusted certificate authorities for SSL** under **Site management**.
>If your system does not trust the certificate you will encounter the error: `certificate verify failed: unable to get local issuer certificate`.
>
>Also do not block the communications to:
>- https://login.microsoftonline.com
>- https://graph.microsoft.com

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

**API Permissions**: At least *GroupMember.Read.All* (Application permission)

**Endpoint**: `https://graph.microsoft.com/v1.0/groups`

---

### Microsoft 365 Licenses

#### Description

This check monitors all the Microsoft 365 licenses available in your Microsoft 365 Tenant. 
Only licenses with a `capabilityStatus` of `warning` or `enabled` are displayed.

| State | Description |
| -------- | ------- |
| `Enabled` | The count of units that are currently active for the service SKU subscription. |
| `lockedOut` | The count of units that are inaccessible due to the customer canceling their service SKU subscription. |
| `suspended` | The count of units that are on hold because the service SKU subscription was canceled. These units cannot be assigned but can be reactivated before deletion. |
| `warning` | The count of units in a warning state. After the service SKU subscription expires, the customer has a grace period to renew before it is canceled and moved to a suspended state. |

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/72522c4c-9fa9-4a1d-bcb9-7f992b9611e2)

#### Checkmk Parameters

1. **Licenses lower levels**: Set lower-level thresholds for the number of remaining available app licenses as absolute or percentage values. To ignore the remaining available licenses, Select "Percentage" or "Absolute" and "No levels".

#### Microsoft Graph API

**API Permissions**: At least *Organization.Read.All* (Application permission)

**Endpoint**: `https://graph.microsoft.com/v1.0/subscribedSkus`

---

### Microsoft 365 Service Health

#### Description

This check monitors the service health status from a Microsoft 365 Tenant. 
Only licensed services are displayed.

The check uses the SKU name as the service name.
To find the corresponding product name, go to https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/eb7c23d1-abf4-4278-8b45-80fe2674858a)

#### Checkmk Parameters

1. **Severity Level Incident**: Set the severity level of the issue type incident. The default severity level is critical.
2. **Severity Level Advisory**: Set the severity level of the issue type advisory. The default severity level is warning.

#### Microsoft Graph API

**API Permissions**: At least *ServiceHealth.Read.All* (Application permission)

**Endpoint**: `https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/healthOverviews`
- Get all licensed services from the Microsoft 365 Tenant.

**Endpoint**: `https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/issues`
- Get all active Microsoft 365 health issues

## Steps to Get It Working

To use this Checkmk Special Agent, you must configure a Microsoft Entra application to access the Microsoft Graph API endpoints.
You must also have a host in Checkmk and configure the Special Agent rule for the host.

### Microsoft Entra Configuration
#### Register an Application

1. Sign in to the Microsoft Entra Admin Center (https://entra.microsoft.com) as a Global Administrator (or at least a Privileged Role Administrator)
2. Browse to **Identity** > **Applications** > **App registrations**
3. Select **New registration**
4. Provide a meaningful name (e.g. "Checkmk Special Agent")
5. Select **Accounts in this organizational directory only**
6. Do not specify a **Redirect URI**
7. Click **Register**

> [!NOTE]
> In the overview of your new application registration, you will find the **Application (client) ID** and the **Directory (tenant) ID**.
> You will need this information later for the configuration of the Checkmk Special Agent.

#### Configure the Application
1. Go to **API permissions**
2. Click **Add a permission** > **Microsoft Graph** > **Application permissions**
3. Add all API permissions for all services that you want to monitor (see sections above)
4. Select **Grant admin consent** > **Yes**
5. Go to **Certificates & secrets** and click **New client secret**
6. Enter a description (e.g. the Checkmk Site name) and select an expiration period for the secret

### Checkmk Special Agent Configuration

1. Log in to your Checkmk site

#### Add a New Password

1. Browse to **Setup** > **Passwords**
2. Select **Add password**
3. Specify a **Unique ID** and a **Title**
4. Copy the generated secret from the Microsoft Entra Admin Center to the **Password** field
5. Click **Save**

#### Add Checkmk Host

1. Add a new host in **Setup** > **Hosts**
2. Configure your custom settings and set
    -   **IP address family**: No IP
    -   **Checkmk agent / API integrations**: API integrations if configured, else Checkmk agent
3. Save

#### Add Special Agent Rule

1. Navigate to the Special Agent rule **Setup** > **Microsoft 365** (use the search bar)
2. Add a new rule and configure the required settings
    -   **Application (client) ID** and **Directory (tenant) ID** from the Microsoft Entra Application
    -   For **Client Secret** select **From password store** and the password from **Add a New Password**
    -   Select all services that you want to monitor
    -   Add the newly created host in **Explicit hosts**
3. Save and go to your new host and discover your new services
4. Activate the changes
