For api overview and usages, check out [this page](overview.md).

[TOC]

# Authentication

## Login

```
POST /api/auth/login
```

**Parameters**

Name              | Data Type | Required | Default Value  | Discription
------------------|-----------|----------|----------------|--------------------
email             | text      | true     | null           | email of the user.
password          | text      | true     | null           | password of the user.
first_name        | text      | false    | ''             | first name of the user.
last_name         | text      | false    | ''             | last name of the user.
gender            | choices   | false    | 'not_selected' | gender of the user.
tshirt_size       | choices   | false    | 'not_selected' | tshirt size of the user.
ticket_id         | uuid      | false    | *uuid          | ticket id of the ticket alloted to user.
phone_number      | text      | false    | ''             | mobile number of the user.
is_core_organizer | boolean   | false    | false          | designates whether the user is a core organizer.
is_volunteer      | boolean   | false    | false          | designates whether the user is a volunteer.
date_joined       | datetime  | false    | *date_time     | date and time when the user registered.
is_active         | boolean   | false    | true           | designates whether the user is active.
is_staff          | boolean   | false    | false          | designates whether the user is staff.
is_superuser      | boolean   | false    | false          | designates whether the user is a superuser

__NOTE__
- *uuid: randomly generated uuid.
- *date_time: date and time when the user gets registered.
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
    "ticket_id": "6659577a-e4e5-4442-bf67-4b4c890d440b",
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
    "ticket_id": "6659577a-e4e5-4442-bf67-4b4c890d440b",
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
    "ticket_id": "6659577a-e4e5-4442-bf67-4b4c890d440b",
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
- User can update any attribute except the following `read_only_fields` - `id`, `ticket_id`, `is_core_organizer`, `is_volunteer`, `date_joined`, `is_active`, `is_staff`, `is_superuser`

**Request**
```json
{
    "id": "629b1e03-53f0-43ef-9a03-17164cf782ac",
    "first_name": "James",
    "last_name": "Warner",
    "email": "james@example.com",
    "gender": "M",
    "tshirt_size": "XL",
    "ticket_id": "6659577a-e4e5-4442-bf67-4b4c890d440b",
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
    "ticket_id": "6659577a-e4e5-4442-bf67-4b4c890d440b",
    "phone_number": "+911234567890",
    "is_core_organizer": false,
    "is_volunteer": false,
    "date_joined": "2018-09-10T19:26:06.217889Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
}
```

# Proposals

## Create Proposal

```
POST /api/proposals
```

**Parameters**

Name               | Data type     | Required | Description
-------------------|---------------|----------|---------------------
id                 | UUID          | false    | Unique ID for the proposal
title              | text          | true     | Title of proposal
speaker            | text          | false    | Speaker for the talk
kind               | text          | true     | Type of proposal like talk, dev sprint, workshop
level              | text          | true     | Level of proposal beginner, intermediate, advanced
duration           | text          | true     | Duration of talk, sprint or workshop, format: hh:mm:ss
abstract           | text          | true     | Abstract of the proposal
description        | text          | true     | Description of the proposal
submitted_at       | datetime      | false    | Time of submission of proposal
approved_at        | datetime      | false    | Time of approval
modified_at        | datetime      | false    | Time of modification
status             | text          | false    | Status of proposal like `retracted`, `accepted`, `unaccepted`, `submitted`, etc.

__NOTE__
- *uuid: randomly generated uuid.
- *date_time: date and time when the proposal is submitted/approved/modified
- Error out in case of invalid duration format.
- Error out in case of missing **required** attributes.

**Request**
```json
{
    "title": "Sample title of the talk",
    "kind": "talk",
    "level": "beginner",
    "duration": "01:30:00",
    "abstract": "This is the abstract of the talk",
    "description": "This is the description of the of the talk and can be quite long"
}
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "title": "Sample title of the talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "kind": "talk",
    "level": "beginner",
    "duration": "01:30:00",
    "abstract": "This is the abstract of the talk",
    "description": "This is the description of the of the talk and can be quite long",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": null,
    "modified_at": "2018-08-01T17:30:42Z",
    "status": "submitted"
}
```

## Update proposal details

```
PATCH /api/proposals/:id (request authentication)
```

**Request**
```json
{
    "title": "Corrected title of talk",
    "level": "advanced"
}
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "title": "Corrected title of talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "kind": "talk",
    "level": "advanced",
    "duration": "01:30:00",
    "abstract": "This is the abstract of the talk",
    "description": "This is the description of the of the talk and can be quite long",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": null,
    "modified_at": "2018-08-03T09:20:00Z",
    "status": "submitted"
}
```

## Accept the proposal

```
POST /api/proposals/:id/accept
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "title": "Corrected title of talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "kind": "talk",
    "level": "advanced",
    "duration": "01:30:00",
    "abstract": "This is the abstract of the talk",
    "description": "This is the description of the of the talk and can be quite long",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-03T09:20:00Z",
    "status": "accepted"
}
```

## Get proposal details

```
GET /api/proposals/:id
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "title": "Corrected title of talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "kind": "talk",
    "level": "advanced",
    "duration": "01:30:00",
    "abstract": "This is the abstract of the talk",
    "description": "This is the description of the of the talk and can be quite long",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-03T09:20:00Z",
    "status": "submitted"
}
```

## Retract the proposal

```
POST /api/proposals/:id/retract (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "title": "Corrected title of talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "kind": "talk",
    "level": "advanced",
    "duration": "01:30:00",
    "abstract": "This is the abstract of the talk",
    "description": "This is the description of the of the talk and can be quite long",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-03T09:20:00Z",
    "status": "retracted"
}
```
