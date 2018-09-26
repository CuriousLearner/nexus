<style>
    .container h1{font-size: 1.5em; }
    .container h2{font-size: 1.2em; }
    .container hr{margin-top: 5px; }
</style>

## Sep 27, 2018

- Add an app for `proposals`. ([@storymode7])
  This adds following endpoints:
  - /api/proposals allowing `POST`, `PATCH`, `GET`
  - /api/proposals/:id which allows to view a specific proposals (`GET`)
  - /api/proposals/:id/retract to retract a proposal (`POST`)
  - /api/proposals/:id/accept to accept a proposal (`POST`)

## Sep 7, 2018

- Add new attributes in `users` app and update related API ([@GeekyShacklebolt])

## Sep 1, 2018

- Add basic code quality pre-commit hooks ([@CuriousLearner])

[@CuriousLearner]: https://github.com/CuriousLearner
[@GeekyShacklebolt]: https://github.com/GeekyShacklebolt
[@storymode7]: https://github.com/storymode7
