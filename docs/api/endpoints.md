For api overview and usages, check out [this page](overview.md).

[TOC]

# Authentication

## Login

```
POST /api/auth/login
```

**Parameters**

Name              | Data Type  | Description
------------------|------------|------------------------
email             | text       | **(required)** email of the user.
password          | text       | **(required)** password of the user.
first_name        | text       | first name of the user.
last_name         | text       | last name of the user.
gender            | choices    | gender of the user.
tshirt_size       | choices    | tshirt size of the user.
ticket_id         | text       | ticket id of the ticket alloted to user.
phone_number      | text       | mobile number of the user.
is_core_organizer | boolean    | designates whether the user is a core organizer.
is_volunteer      | boolean    | designates whether the user is a volunteer.
date_joined       | datetime   | date and time when the user registered.
is_active         | boolean    | designates whether the user is active.
is_staff          | boolean    | designates whether the user is staff.
is_superuser      | boolean    | designates whether the user is a superuser

__NOTE__
- Error out in case of invalid email/password.
- Error out in case of missing **required** attributes.

**Request**
```json
{
    "email": "hello@example.com",
    "password": "VerySafePassword0909"
}
```

**Response**
Status: 200 OK
```json
{
    "id": "171956bd-717f-4021-a901-c5be80fd469b",
    "first_name": "John",
    "last_name": "Howley",
    "email": "hello@example.com",
    "gender": "NA",
    "tshirt_size": "NA",
    "ticket_id": "Not assigned",
    "phone_number": "",
    "is_core_organizer": false,
    "is_volunteer": false,
    "date_joined": "2018-09-10T19:26:06.217889Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "auth_token": "AkJ0b.Ai0iJEv1EiLCJhbGciOiJIUeI1NiJ9.eyJ1c2VyX2F1dGhlbnRpY2F0eW9uX2lEIjoiMTcxOTU2YmEtNe3Ai00MDIxLWe5MDetYeViATgwemE0NjliIn0.loCdI3te2sICj8e5c6ip5TW_eFNn5RTj4HU-e2q0m"
}
```

## Register

```
POST /api/auth/register
```

__NOTE__
- Error out if email is already registered.

**Request**
```json
{
    "email": "hello@example.com",
    "password": "VerySafePassword0909",
    "first_name": "John",
    "last_name": "Howley",
    "gender": "M",
    "tshirt_size": "L",
    "phone_number": "+911234567890"
}
```

**Response**
Status: 201 Created
```json
{
    "id": "1f19560d-f1ff-4021-a901-c50e80fd4690",
    "first_name": "John",
    "last_name": "Howley",
    "email": "hello@example.com",
    "gender": "M",
    "tshirt_size": "L",
    "ticket_id": "Not assigned",
    "phone_number": "+911234567890",
    "is_core_organizer": false,
    "is_volunteer": false,
    "date_joined": "2018-09-10T19:26:06.217889Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "auth_token": "eyJ0aXAiOiJqV1QiLCJhbGciOiJIUaI1NiJ9.ayJ1c2VyX2F1dGhlbnRpY2F0aW9uX2lqIjoiMTcxOTU2YmQtNa3ai00MDIxLWa5MDatYaViaTgwamQ0NjliIn0.loCdI3tAa2sICj8a5c6ip5TW_aFnn5RTj4HU-D6zq3c"
}
```

## Change password

```
POST /api/auth/password_change (requires authentication)
```

**Parameters**

Name             | Description
-----------------|-------------------------------------
current_password | Current password of the user.
new_password     | New password of the user.

**Request**
```json
{
    "current_password": "NotSoSafePassword",
    "new_password": "VerySafePassword0909"
}
```

**Response**
Status: 204 No-Content

## Request password for reset

Send an email to user if the email exist.

```
POST /api/auth/password_reset
```

**Parameters**

Name  | Description
------|-------------------------------------
email | (required) valid email of an existing user.

**Request**
```json
{
    "email": "hello@example.com"
}
```

**Response**
Status: 200 OK
```json
{
    "message": "Further instructions will be sent to the email if it exists"
}
```


## Confirm password reset

Confirm password reset for the user using the token sent in email.

```
POST /api/auth/password_reset_confirm
```

**Parameters**

Name          | Description
--------------|-------------------------------------
new_password  | New password of the user
token         | Token decoded from the url (verification link)


**Request**
```json
{
    "new_password": "new_pass",
    "token" : "IgotTHISfromTHEverificationLINKinEmail"
}
```

**Response**
Status: 204 No-Content

__Note__
- The verification link uses the format of key `password-confirm` in `FRONTEND_URLS` dict in settings/common.


# Current user actions

## Get profile of current logged-in user
```
GET /api/me (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "id": "629b1e03-53f0-43ef-9a03-17164cf782ac",
    "first_name": "John",
    "last_name": "Howley",
    "email": "hello@example.com",
    "gender": "NA",
    "tshirt_size": "NA",
    "ticket_id": "Not assigned",
    "phone_number": "",
    "is_core_organizer": false,
    "is_volunteer": false,
    "date_joined": "2018-09-10T19:26:06.217889Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
}
```

## Update profile of current logged-in user
```
PATCH /api/me (requires authentication)
```

__NOTE__
- Complete resource goes in request but a user itself is not allowed to update `read_only_fields` viz. `id`, `ticket_id`, `is_core_organizer`, `is_volunteer`, `date_joined`, `is_active`, `is_staff`, `is_superuser`

**Request**
```json
{
    "id": "629b1e03-53f0-43ef-9a03-17164cf782ac",
    "first_name": "James",
    "last_name": "Warner",
    "email": "james@example.com",
    "gender": "M",
    "tshirt_size": "XL",
    "ticket_id": "Not assigned",
    "phone_number": "+91123456789",
    "is_core_organizer": false,
    "is_volunteer": false,
    "date_joined": "2018-09-10T19:26:06.217889Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
}
```

**Response**
Status: 200 OK
```json
{
    "id": "629b1e03-53f0-43ef-9a03-17164cf782ac",
    "first_name": "James",
    "last_name": "Warner",
    "email": "james@example.com",
    "gender": "M",
    "tshirt_size": "XL",
    "ticket_id": "Not assigned",
    "phone_number": "+911234567890",
    "is_core_organizer": false,
    "is_volunteer": false,
    "date_joined": "2018-09-10T19:26:06.217889Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
}
```
