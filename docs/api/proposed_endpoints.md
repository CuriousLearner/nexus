[TOC]

# User Authentication

## Register a user

```
POST /api/auth/register/
```

**Parameters**

Name        | Data Type | Description
------------|-----------|---------------------------
id          | UUID      | Id of the user
first_name  | text      | first name of the user
last_name   | text      | last name of the user
email_id    | text      | email of user. Errors out if email already registered.
password    | text      | Hash of the user's password
gender      | choices   | gender (Like Male, Female, Others)
tshirt_size | choices   | size of the TShirt (Like Small, Medium etc.)
contact     | text      | contact number
ticket_id   | text      | ticket ID generated at registration
created_at  | datetime  | date and time of registration
modified_at | datetime  | date and time of modification
user_type   | choices   | Type of user like admin, volunteer, attendee



**Request**
```json
{
    "id": null,
    "first_name": "John",
    "last_name": "Hawley",
    "email_id": "john@localhost.com",
    "password": "VerySafePassword0909",
    "gender": "Male",
    "tshirt_size": "Medium",
    "contact": "+919999999999",
    "ticket_id": null,
    "created_at": null,
    "modified_at": null,
    "user_type": null
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
    "gender": "Male",
    "tshirt_size": "Medium",
    "contact": "+919999999999",
    "ticket_id": "This-is-a-unique-ticket-id",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z",
    "user_type": "Attendee"
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
    "gender": "Male",
    "tshirt_size": "Extra Large",
    "contact": "+919999999998",
    "ticket_id": "This-is-a-unique-ticket-id",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-02T07:10:42Z",
    "user_type": "Volunteer"
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
    "gender": "Male",
    "tshirt_size": "Extra Large",
    "contact": "+919999999998",
    "user_type": "Volunteer"
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
    "gender": "Male",
    "tshirt_size": "Extra Large",
    "contact": "+919999999998",
    "ticket_id": "This-is-a-unique-ticket-id",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-02T07:10:42Z",
    "user_type": "Volunteer"
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
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_on": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "text": "anything that user has to write",
    "image": null,
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false",
    "posted_time": null
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
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false",
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
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_on": "facebook",
    "text": "some new content",
    "image":"http://xyz.com/url/of/uploaded_image.jpg",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-01T11:00:00Z",
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false",
    "posted_time": null
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
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false",
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
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false",
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
    "is_approved": "true",
    "approved_time": "2018-09-05T15:20:00Z",
    "is_posted": "false",
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
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false",
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
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false",
    "posted_time": null
}
```

# Talks

## Create Talk

```
POST /api/talk 
```

**Parameters**

Name               | Data type     | Description
-------------------|---------------|---------------------
id                 | UUID          | Unique ID for the talk
talk_name          | text          | Name of talk
speaker            | text          | Speaker for the talk
type               | choices       | Type like talk, dev sprint, workshop
level              | choices       | Level of talk beginner, intermediate, advanced
duration           | text          | Duration of talk 
submitted_at       | datetime      | Time of submission of talk
approved_at        | datetime      | Time of talk approval
modified_at        | datetime      | Time of modification
proposed_time      | datetime      | Proposed time of talk
talk_status        | choices       | Status of talk like retracted, accepted, unaccepted, submitted, etc.


**Request**
```json
{
    "id": null,
    "talk_name": "Sample name of the talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "type": "talk",
    "level": "beginner",
    "duration": "1Hours 30Minutes",
    "submitted_at": null,
    "approved_at": null,
    "modified_at": null,
    "proposed_time": "2018-10-10T11:10:00:00Z",
    "talk_status": null
}
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "talk_name": "Sample name of the talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "type": "talk",
    "level": "beginner",
    "duration": "1Hours 30Minutes",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": null,
    "modified_at": "2018-08-01T17:30:42Z",
    "proposed_time": "2018-10-10T11:10:00:00Z",
    "talk_status": "submitted"
}
```

## Update talk details

```
PATCH /api/talk/:id (request authentication)
```

**Request**
```json
{
    "talk_name": "Corrected name of talk",
    "level": "advanced"
}
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "talk_name": "Corrected name of talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "type": "talk",
    "level": "advanced",
    "duration": "1Hours 30Minutes",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": null,
    "modified_at": "2018-08-03T09:20:00Z",
    "proposed_time": "2018-10-10T11:10:00:00Z",
    "talk_status": "submitted"
}
```

## Accept the talk

```
POST /api/talk/:id/accept
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "talk_name": "Corrected name of talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "type": "talk",
    "level": "advanced",
    "duration": "1Hours 30Minutes",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-03T09:20:00Z",
    "proposed_time": "2018-10-10T11:10:00:00Z",
    "talk_status": "accepted"
}
```

## Get talk details

```
GET /api/talk/:id
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "talk_name": "Corrected name of talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "type": "talk",
    "level": "advanced",
    "duration": "1Hours 30Minutes",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-03T09:20:00Z",
    "proposed_time": "2018-10-10T11:10:00:00Z",
    "talk_status": "submitted"
}
```

## Retract the talk

```
PATCH /api/talk/:id/retract (requires authentication)
```

**Response**
Status: 201 Created
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "talk_name": "Corrected name of talk",
    "speaker": "070af5d3-03a1-4a38-9a75-5b76de8826d2",
    "type": "talk",
    "level": "advanced",
    "duration": "1Hours 30Minutes",
    "submitted_at": "2018-08-01T17:30:42Z",
    "approved_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-03T09:20:00Z",
    "proposed_time": "2018-10-10T11:10:00:00Z",
    "talk_status": "retracted"
}
```

