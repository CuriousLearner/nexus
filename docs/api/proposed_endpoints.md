[TOC]

# User Authentication

## Register a user

```
POST /api/auth/register/
```

**Parameters**

Name              | Data Type | Description
------------------|-----------|---------------------------
id                | UUID      | Id of the user
first_name        | text      | first name of the user
last_name         | text      | last name of the user
email_id          | text      | email of user. Errors out if email already registered.
password          | text      | Hash of the user's password
gender            | text      | gender (Like `male`, `female`, `others`)
tshirt_size       | text      | size of the TShirt (Like `small`, `medium`, `large`, `extra_large` etc.)
contact           | text      | contact number
ticket_id         | text      | ticket ID generated at registration
created_at        | datetime  | date and time of registration
modified_at       | datetime  | date and time of modification
is_core_organizer | boolean   | true if the user is a core organizer
is_volunteer      | boolean   | true if the user is a volunteer


**Request**
```json
{
    "id": null,
    "first_name": "John",
    "last_name": "Hawley",
    "email_id": "john@localhost.com",
    "password": "VerySafePassword0909",
    "gender": "male",
    "tshirt_size": "medium",
    "contact": "+919999999999",
    "ticket_id": null,
    "created_at": null,
    "modified_at": null,
}
```


**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "first_name": "John",
    "last_name": "Hawley",
    "email_id": "john@localhost.com",
    "auth_token": "eyJ0eXAi0iJKV1QiLCJh",
    "gender": "male",
    "tshirt_size": "medium",
    "contact": "+919999999999",
    "ticket_id": "This-is-a-unique-ticket-id",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z",
    "is_core_organizer": false,
    "is_volunteer": false
}
```

# Current user actions

## Get current logged-in user's details

```
GET /api/me (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "first_name": "Jaun",
    "last_name": "Hawley",
    "email_id": "jaun@localhost.com",
    "gender": "male",
    "tshirt_size": "extra_large",
    "contact": "+919999999998",
    "ticket_id": "This-is-a-unique-ticket-id",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-02T07:10:42Z",
    "is_core_organizer": false,
    "is_volunteer": false
}
```

## Update user details

```
PATCH /api/me (requires authentication)
```

**Request**
```json
{
    "first_name": "Jaun",
    "last_name": "Hawley",
    "email_id": "jaun@localhost.com",
    "gender": "male",
    "tshirt_size": "extra_large",
    "contact": "+919999999998",
}
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "first_name": "Jaun",
    "last_name": "Hawley",
    "email_id": "jaun@localhost.com",
    "gender": "male",
    "tshirt_size": "extra_large",
    "contact": "+919999999998",
    "ticket_id": "This-is-a-unique-ticket-id",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-02T07:10:42Z",
    "is_core_organizer": false,
    "is_volunteer": false
}
```

## Delete User

```
DELETE /api/me (requires authentication)
```

__NOTE__: This will be a soft-delete.

**Response**
Status: 204 No-Content

# Social Media Posts

## Create a post

```
POST /api/posts (requires authentication)
```

**Parameters**

Name          | Data Type   | Description
--------------|-------------|------------------------------------------
id            | UUID        | identity of the post
posted_by     | UUID        | foreign key to `Users` model
posted_on     | text        | social media ploatform to post
created_at    | datetime    | time at which user submits the post
modified_at   | datetime    | time at which the post is modified/updated
scheduled_time| datetime    | time that the user schedules for his post to be posted
text          | text        | content of the post
image         | text        | url of image in the post
is_approved   | boolean     | whether the post is approved or not
approved_time | datetime    | time at which the post is approved
is_posted     | boolean     | whether the post is posted or not
posted_time   | datetime    | time at which the post will be posted

**Request**
```json
{
    "posted_on": "twitter",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "text": "anything that user has to write",
}
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_on": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "text": "anything that user has to write",
    "image": null,
    "is_approved": false,
    "approved_time": null,
    "is_posted": false,
    "posted_time": null

}
```

## Update a post

```
PATCH /api/posts/:post_id (requires authentication)
```

**Request**
```json
{
    "posted_on": "facebook",
    "text": "some new content",
    "image":"http://xyz.com/url/of/uploaded_image.jpg",
    "scheduled_time": "2018-10-01T11:00:00Z",
}
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_on": "facebook",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "text": "some new content",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": false,
    "approved_time": null,
    "is_posted": false,
    "posted_time": null
}
```

## Review a post

```
GET /api/posts/:post_id
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_on": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "text": "anything that user has to write",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": false,
    "approved_time": null,
    "is_posted": false,
    "posted_time": null
}
```

## Approving a post

```
POST /api/posts/:post_id/approve (requires authentication)
```

__NOTE__:Only an Admin or a Moderator can approve a post.

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_on": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "text": "anything that user has to write",
    "image": "http://xyz.com/url/to/uploaded_image.jpg",
    "is_approved": true,
    "approved_time": "2018-09-05T15:20:00Z",
    "is_posted": false,
    "posted_time": null
}
```

## Deleting a post

```
DELETE /api/posts/:post_id (requires authentication)
```

**Response**
Status: 204 No-Content

## Add an image to the social media post

```
POST /api/posts/:post_id/upload_image (requires authentication)
```

Image will be uploaded as multipart data as a streaming HTTP request.

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_on": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "text": "anything that user has to write",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": false,
    "approved_time": null,
    "is_posted": false,
    "posted_time": null
}
```

## Delete the image from social media post

```
DELETE /api/posts/:post_id/delete_image (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_on": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "text": "anything that user has to write",
    "image": null,
    "is_approved": false,
    "approved_time": null,
    "is_posted": false,
    "posted_time": null
}
```

# Proposals

## Create Proposal

```
POST /api/proposals (requires authentication)
```

**Parameters**

Name               | Data type     | Description
-------------------|---------------|---------------------
id                 | UUID          | Unique ID for the proposal
title              | text          | Title of proposal
speaker            | UUID          | ID of a `User`
kind               | text          | Type of proposal like `talk`, `dev sprint`, `workshop` or `lightning_talk`
level              | text          | Level of proposal beginner, intermediate, advanced
duration           | text          | Duration of the `talk`, `sprint`, `workshop` or `lightning talk`
abstract           | text          | Abstract of the proposal
description        | text          | Description of the proposal
submitted_at       | datetime      | Time of submission of proposal
approved_at        | datetime      | Time of approval
modified_at        | datetime      | Time of modification
status             | text          | Status of proposal like `retracted`, `accepted`, `unaccepted`, `submitted`, etc.

__Note__:
- For `lightning_talk`, duration will be fixed like `00:05:00`, etc. which would be configuration through settings.
- For `lightning_talk`, key `level` would be treated as speaker's experience, which can be `beginner`, `intermediate` or `advanced`.

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
PATCH /api/proposals/:id (requires authentication)
```

**Request**
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "title": "Sample title of the talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "kind": "talk",
    "level": "advanced",
    "duration": "01:30:00",
    "abstract": "This is the abstract of the talk",
    "description": "This is the description of the of the talk and can be quite long",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": null,
    "modified_at": "2018-08-01T17:30:42Z",
    "status": "submitted"
}
```

__Note__: Non-staff users are allowed to update only following fields:
    - title
    - kind
    - level
    - duration
    - abstract
    - description

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
POST /api/proposals/:id/accept (requires authentication)
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
GET /api/proposals/:id (requires authentication)
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

## Send notification to individual speaker

```
POST /api/proposals/:id/notify (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "message": "Notification of proposal accepted will be sent to the speaker."
}
```

__Note__:
- Notification will be sent only if the `status` of the proposal is `accepted`.

## Send notification to all the speakers

```
POST /api/proposals/notify (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "message": "Notification of proposal accepted will be sent to all the speakers."
}
```

__Note__:
- Notification will be sent only if the `status` of the proposal is `accepted`.

# Swags

**Parameters**

Name              | Data Type | Required | Default Value  | Discription
------------------|-----------|----------|----------------|--------------------
id                | UUID      | false    | _uuid_         | Unique ID for the swag.
name              | text      | true     | ''             | Name of the swag.
description       | text      | false    | ''             | Description of the swag.
image             | text      | false    | ''             | URL of the image of the swag.
created_at        | datetime  | false    | _datetime_     | Time of creation.
modified_at       | datetime  | false    | _datetime_     | Time of last modification.

__Note__:
- _uuid_: Randomly generated Universally Unique IDentifier (UUID).
- _datetime_: Date and time when `Swag` is created.

## Create a swag

```
POST /api/swags (requires authentication)
```

**Request**
```json
{
    "name": "tshirt",
    "description": "sponsered by someone"
}
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "name": "tshirt",
    "description": "sponsered by someone",
    "image": null,
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z"
}
```

## Update swag details

```
PATCH /api/swags/:id (requires authentication)
```

**Request**
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "name": "pendrive",
    "description": "sponsered by someone else",
    "image": null,
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z"
}
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "name": "pendrive",
    "description": "sponsered by someone else",
    "image": null,
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z"
}
```

## Get swag details

```
GET /api/swags/:id (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "name": "tshirt",
    "description": "sponsered by someone",
    "image": null,
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z"
}
```

## Get details of all the swags

```
GET /api/swags (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
            "name": "tshirt",
            "description": "sponsered by someone",
            "image": null,
            "created_at": "2018-08-01T17:30:42Z",
            "modified_at": "2018-08-01T17:30:42Z"
        }
    ]
}
```

## Delete a swag

```
DELETE /api/swags/:id (requires authentication)
```

**Response**
Status: 204 No-Content

## Upload image of a swag

```
POST /api/swags/:id/upload_image (requires authentication)
```

Image will be uploaded as multipart data as a streaming HTTP request.

__Note__:
- `image` key will be used to send multipart data.

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "name": "tshirt",
    "description": "sponsered by someone",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z"
}
```

## Delete the image of swag

```
DELETE /api/swags/:id/delete_image (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "name": "tshirt",
    "description": "sponsered by someone",
    "image": null,
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z"
}
```

# User-Swag Relation

`UserSwag` relation is used to keep the account of which swag(s) is/are given to a `User`.

**Parameters**

Name              | Data Type | Required | Default Value  | Discription
------------------|-----------|----------|----------------|--------------------
id                | UUID      | false    | _uuid_         | Unique ID for each `UserSwag` entry.
user              | UUID      | true     | ''             | ID of the `User`.
swag              | UUID      | true     | ''             | ID of the `Swag`.
created_at        | datetime  | false    | _datetime_     | Time of creation.
modified_at       | datetime  | false    | _datetime_     | Time of modification.

__Note__:
- _uuid_: Randomly generated Universally Unique IDentifier (UUID).
- _datetime_: Date and time when the `UserSwag` object is created.

## Create a new user-swag entry

```
POST /api/user_swags (requires authentication)
```

**Request**
```json
{
    "user": "6659577a-e4e5-4442-bf67-4b4c890d440b",
    "swag": "171956bd-717f-4021-a901-c5be80fd469b"
}
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "user": "6659577a-e4e5-4442-bf67-4b4c890d440b",
    "swag": "171956bd-717f-4021-a901-c5be80fd469b",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z"
}
```

__Note__:
- Presence of a `UserSwag` entry indicates that, the `Swag` is given to the `User`.
- And the key `created_at` indicates the time when `Swag` is given to the `User`.

## Get user-swag entry details

```
GET /api/user_swags/:id (requires authentication)
```

**Response**
Status: 200 OK
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "user": "6659577a-e4e5-4442-bf67-4b4c890d440b",
    "swag": "171956bd-717f-4021-a901-c5be80fd469b",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z"
}
```

## Get details of all the user-swag entries

```
GET /api/user_swags
```

**Response**
Status: 200 OK
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
            "user": "6659577a-e4e5-4442-bf67-4b4c890d440b",
            "swag": "171956bd-717f-4021-a901-c5be80fd469b",
            "created_at": "2018-08-01T17:30:42Z",
            "modified_at": "2018-08-01T17:30:42Z"
        }
    ]
}
```

## Delete a user-swag entry

```
DELETE /api/user_swags/:id (requires authentication)
```

**Response**
Status: 204 No-Content
