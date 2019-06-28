<style>
    .container h1{font-size: 1.5em; }
    .container h2{font-size: 1.2em; }
    .container hr{margin-top: 5px; }
</style>

## Jun 29, 2019

- Add feature to publish social media post on twitter ([@GeekyShacklebolt])

## Jun 26, 2019

- Add feature to publish social media post on facebook ([@storymode7])

## Mar 5, 2019

- Remove endpoint: publish a post via `POST /api/posts/:post_id/publish` ([@GeekyShacklebolt])
- Add endpoint: unapprove a post via `POST /api/posts/:post_id/unapprove` ([@GeekyShacklebolt])

## Dec 15, 2018
- Add an app for `posts`. ([@realslimshanky])
  This adds following features:
  - Get list of all posts via `GET /api/posts`
  - Add new post via `POST /api/posts`
  - Get post details via `GET /api/posts/:post_id`
  - Update a post via `PATCH /api/posts/:post_id`
  - Delete a post via `DELETE /api/posts/:post_id`
  - Approve a post via `POST /api/posts/:post_id/approve`
  - Publish a post via `POST /api/posts/:post_id/publish`
  - Upload/update an image via `POST /api/posts/:post_id/upload_image`
  - Delete image in post via `POST /api/posts/:post_id/delete_image`

## Sep 27, 2018

- Add an app for `proposals`. ([@storymode7])
  This adds following features:
  - Get list of all proposals via `GET /api/proposals`
  - Get proposal details via `GET /api/proposals/:id`
  - Update a proposal via `PATCH /api/proposals/:id`
  - Retract a proposal via `POST /api/proposals/:id/retract`
  - Accept a proposal via `POST/api/proposals/:id/accept`

## Sep 7, 2018

- Add new attributes in `users` app and update related API ([@GeekyShacklebolt])

## Sep 1, 2018

- Add basic code quality pre-commit hooks ([@CuriousLearner])

[@CuriousLearner]: https://github.com/CuriousLearner
[@GeekyShacklebolt]: https://github.com/GeekyShacklebolt
[@storymode7]: https://github.com/storymode7
