# Trackmania TOTD Discord Bot

## Setup

### Configuration

Using `.env.template`, create a file called `.env` and fill in your credentials. This is required for the bot to run.

### Dependencies

This repo uses `pipenv` for its dependency management. See the docs [here](https://pipenv.pypa.io/en/latest/).

Initially, run `pipenv install` to install the dependencies.

Then, you can either use `pipenv run python [file]` or `pipenv shell` to create a subshell in which you can run your python commands.

To add new dependencies, simply run `pipenv install [dependency]`. Add a `--dev` flag if it's a development dependency.
