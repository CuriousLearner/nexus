[TOC]

# Posts related actions

## Create a post

Create a post of contents.

```
POST /api/posts (requires authentication)
```

**Parameters**

Name          | Data Type   | Description
--------------|-------------|------------------------------------------
id            | UUID        | identity of the post
posted_by     | UUID        | Foreign key to `Users` model
posted_at     | text        | social media ploatform to post
created_at    | datetime    | time at which user submits the post
modified_at   | datetime    | time at which post is modified/updated
scheduled_time| datetime    | time at which the post is scheduled to be posted
text          | text        | content of the post
image         | text        | url of image in the post
is_approved   | boolean     | whether the post is approved or not
approved_time | datetime    | time at which the post is approved
is_posted     | boolean     | whether the post is posted or not

**Request**
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_at": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z",
    "scheduled_time": null,
    "text": "anything that user has to write",
    "image": null,
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false"
}
```

**Response**
```json

Status: 201 Created
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_at": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-08-01T17:30:42Z",
    "scheduled_time": null,
    "text": "anything that user has to write",
    "image": null,
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false"

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
    "posted_at": "facebook",
    "text": "Some new content",
    "image":"http://xyz.com/url/of/uploaded_image.jpg",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-10T13:43:42Z",
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false"
}
```

**Response**
```json

Status: 200 OK
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_at": "facebook",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-10T13:43:42Z",
    "text": "Some new content",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false"
}
```

## Review a post

```
GET /api/posts/:post_id
```

**Response**
```json

Status: 200 OK
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_at": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-10T13:43:42Z",
    "text": "anything that user has to write",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false"
}
```

## Approving a post (requires authentication)

```
POST /api/posts/:post_id/approve
```

Only an Admin or a Moderator can approve a post.

**Request**
```json
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_at": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-10T13:43:42Z",
    "text": "anything that user has to write",
    "image": "http://xyz.com/url/to/uploaded_image.jpg",
    "is_approved": "true",
    "approved_time": "2018-09-05T15:20:00Z",
    "is_posted": "false"
```

**Response**
```json

Status: 200 OK
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_at": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": "2018-10-10T13:43:42Z",
    "text": "anything that user has to write",
    "image": "http://xyz.com/url/to/uploaded_image.jpg",
    "is_approved": "true",
    "approved_time": "2018-09-05T15:20:00Z",
    "is_posted": "false"
}
```

## Deleting a post

```
DELETE /api/posts/:post_id (requires authentication)
```

**Response**
```json

Status: 204 No-Content
```

## Upload image

```
POST /api/posts/:post_id/upload_image (requires authentication)
```

Image will be uploaded as multipart data as a streaming HTTP request.

**Response**
```json

Status: 201 Created
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "01ade2ff-ab21-231f-a12b3c4d5e79",
    "posted_at": "twitter",
    "created_at": "2018-08-01T17:30:42Z",
    "modified_at": "2018-09-03T14:23:01Z",
    "scheduled_time": null,
    "text": "anything that user has to write",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": "false",
    "approved_time": null,
    "is_posted": "false"
}
```
