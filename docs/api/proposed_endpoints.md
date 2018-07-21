[TOC]

# Posts related actions

## Create a post

Create a post of contents.

```
POST api/posts
```

**Paramaters**

Name         | Description
-------------|--------------------------------------
id           | identity of the post
posted_by    | user who is posting the content
posted_at    | social media ploatform to post
posted_time  | time at which post should be posted
content_type | type of content, text or image
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
    "content_type": "text",
    "content": "Anything that user has to write",
    "image": "",
    "is_approved": "False",
    "is_posted": "False"
}
```

**Response**
```json

Status: 201 Created
{
    "id": "724",
    "posted_by": "John Micky",
    "posted_at": "Twitter",
    "posted_time": "",
    "content_type": "text",
    "content": "Anything that user has to write",
    "image": "http://xyz.com/path/of/image.jpg",
    "is_approved": "False",
    "is_posted": "False"

}
```

## Update a post

```
PATCH api/posts/:post_id (Requires Authorization)
```

**Parameters**

Name         | Description
-------------|--------------------------------------
new_content  | new content of the post
new_image    | new image in the post
posted_time  | time at which post should be posted
content_type | current content type of the post

**Request**
```json
{
    "new_content": "",
    "new_image":"http://xyz.com/path/of/image.jpg",
    "posted_time": "2018-10-10T13:43:42Z",
    "content_type": "image"
}
```

**Response**
```json

Status: 200 OK
{
    "id": "724",
    "posted_by": "John Micky",
    "posted_at": "Twitter",
    "posted_time": "2018-10-10T13:43:42Z",
    "content_type": "image",
    "content": "",
    "image": "http://xyz.com/path/of/image.jpg",
    "is_approved": "False",
    "is_posted": "False"
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
    "posted_at": "Twitter",
    "posted_time": "2018-10-10T13:43:42Z",
    "content_type": "text",
    "content": "Anything that user has to say",
    "image": "",
    "is_approved": "False",
    "is_posted": "False"
}
```

## Approving a post

```
PATCH api/posts/:post_id/approve
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

## Deleting a post

```
DELETE api/posts/:post_id
```

**Response**
```json

Status: 204 No-Content
```

## Upload image

```
POST api/image
```

**Paramaters**

Name         | Description
-------------|--------------------------------------
id           | identity of the post
local_url    | image in the post

**Request**
```json
{
    "id": "724",
    "local_url": "local url of image"
}
```

**Response**
```json

Status: 201 Created
{
    "url": "http://xyz.com/path/of/image.jpg"
}
```

