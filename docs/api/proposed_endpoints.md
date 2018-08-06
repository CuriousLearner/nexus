[TOC]

# Posts related actions

## Create a post

Create a post of contents.

```
POST api/posts (requires authentication)
```

**Parameters**

Name          | Data Type   | Description
--------------|-------------|------------------------------------------
id            | UUID        | identity of the post
posted_by     | text        | authorized user who is posting the content
post_platform | text        | social media ploatform to post
submitted_at  | datetime    | time at which user submits the post
posted_at     | datetime    | time at which post should be posted
content       | text        | content of the post
image         | text        | url of image in the post
is_approved   | boolean     | whether the post is approved or not
is_posted     | boolean     | whether the post is posted or not

**Request**
```json
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "John Micky",
    "post_platform": "Twitter",
    "submitted_at": "2018-08-01T17:30:42Z",
    "posted_at": "null",
    "content": "Anything that user has to write",
    "image": "null",
    "is_approved": "false",
    "is_posted": "false"
}
```

**Response**
```json

Status: 201 Created
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "John Micky",
    "post_platform": "Twitter",
    "submitted_at": "2018-08-01T17:30:42Z",
    "posted_at": "null",
    "content": "Anything that user has to write",
    "image": "null",
    "is_approved": "false",
    "is_posted": "false"

}
```

## Update a post

```
PATCH api/posts/:post_id (requires authentication)
```

**Request**
```json
{
    "posted_by": "John Micky",
    "post_platform": "Facebook",
    "content": "Some new content",
    "image":"http://xyz.com/url/of/uploaded_image.jpg",
    "submitted_at": "2018-09-03T14:23:01Z",
    "posted_at": "2018-10-10T13:43:42Z",
    "is_approved": "false",
    "is_posted": "false"
}
```

**Response**
```json

Status: 200 OK
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "John Micky",
    "post_platform": "Facebook",
    "submitted_at": "2018-09-03T14:23:01Z",
    "posted_at": "2018-10-10T13:43:42Z",
    "content": "Some new content",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": "false",
    "is_posted": "false"
}
```

## Review a post

```
GET api/posts/:post_id
```

**Response**
```json

Status: 200 OK
{
    "posted_by": "John Micky",
    "post_platform": "Twitter",
    "submitted_at": "2018-09-03T14:23:01Z",
    "posted_at": "2018-10-10T13:43:42Z",
    "content": "Anything that user has to say",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": "false",
    "is_posted": "false"
}
```

## Approving a post (requires authentication)

```
PATCH api/posts/:post_id/approve
```

**Response**
```json

Status: 200 OK
{
    "posted_by": "John Micky",
    "post_platform": "Twitter",
    "submitted_at": "2018-09-03T14:23:01Z",
    "posted_at": "2018-10-10T13:43:42Z",
    "content": "Anything that user has to say",
    "image": "http://xyz.com/url/to/uploaded_image.jpg",
    "is_approved": "true",
    "is_posted": "false"
}
```

## Deleting a post

```
DELETE api/posts/:post_id (requires authentication)
```

**Response**
```json

Status: 204 No-Content
```

## Upload image

```
POST api/posts/multipart/image (requires authentication)
```

Image will be uploaded as multipart data as a streaming HTTP request.

**Response**
```json

Status: 201 Created
{
    "id": "0f342ac1-ac32-4bd1-3612-efa32bc3d9a0",
    "posted_by": "John Micky",
    "post_platform": "Twitter",
    "submitted_at": "2018-08-01T17:30:42Z",
    "posted_at": "null",
    "content": "Anything that user has to write",
    "image": "http://xyz.com/url/of/uploaded_image.jpg",
    "is_approved": "false",
    "is_posted": "false"
}
```
