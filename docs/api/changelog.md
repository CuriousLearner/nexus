<style>
    .container h1{font-size: 1.5em; }
    .container h2{font-size: 1.2em; }
    .container hr{margin-top: 5px; }
</style>

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
