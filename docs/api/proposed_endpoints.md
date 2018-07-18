[TOC]

# Posts related actions

## Create a post

Create a post of contents (text + image).

```
POST api/posts/create
```

**Paramaters**

Name         | Description
-------------|--------------------------------------
id           | identity of the post
posted_by    | user who is posting the content
posted_at    | social media ploatform to post
posted_time  | time at which post should be posted
content      | content of the post
image        | image in the post
is_approved  | whether the post is approved or not
is_posted    | whether the post is posted or not

**Request**
```json
{
    "id": "724",
    "posted_by": "John Micky",
    "posted_at": "Twitter",
    "posted_time": "",
    "content": "Anything that user has to write",
    "image": "Uploaded Image",
    "is_approved": "False",
    "is_posted": "False"
}
```

**Response**
```json

Status: 201 Created
{
    "message": "Post is queued and waiting for moderation"
}
```

## Update a post

```
PATCH api/posts/update
```

**Parameters**

Name         | Description
-------------|--------------------------------------
new_content  | new content of the post
new_image    | new image in the post
posted_time  | time at which post should be posted

**Request**
```json
{
    "new_content": "Newly updated content",
    "new_image": "Uploaded image",
    "posted_time": "2018-10-10T13:43:42Z"
}
```

**Response**
```json

Status: 200 OK
{
    "message": "Post is updated"
}
```

## Review a post

```
GET api/posts/review
```

**Request**
```json
{
    "id": "724"
}
```

**Response**
```json

Status: 200 OK
{
    "posted_by": "John Micky",
    "posted_at": "Twitter",
    "posted_time": "2018-10-10T13:43:42Z",
    "content": "Anything that user has to say",
    "image": "Uploaded Image",
    "is_approved": "False",
    "is_posted": "False"
}
```

## Approving a post

```
PATCH api/posts/approve
```

**Request**
```json
{
    "id": "724",
}
```

**Response**
```json

Status: 200 OK
{
    "is_approved": "True",
    "is_posted": "False",
    "posted_time": "2018-10-10T13:43:42Z"
}
```

## Deleting a post

```
DELETE api/posts/delete
```

**Request**
```json
{
    "id": "724"
}
```

**Response**
```json

Status: 200 OK
{
    "message": "Post is deleted"
}
```
