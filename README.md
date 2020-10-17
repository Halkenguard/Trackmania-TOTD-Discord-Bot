# Trackmania TOTD Discord Bot

## Setup

### Configuration

Using `.env.template`, create a file called `.env` and fill in your credentials. This is required for the bot to run.

### Dependencies

This repo uses `pipenv` for its dependency management. See the docs [here](https://pipenv.pypa.io/en/latest/).

Initially, run `pipenv install` to install the dependencies.

Then, you can either use `pipenv run python [file]` or `pipenv shell` to create a subshell in which you can run your python commands.

To add new dependencies, simply run `pipenv install [dependency]`. Add a `--dev` flag if it's a development dependency.

## Ideas for Improvements

- Improve the TOTD message:
  - Show the map's thumbnail. The URL is contained in the map information.
  - Get the TMX thumbnail. Typically, maps on TMX have a stylized thumbnail that's better than the in-game one.
  - Get the map's assigned difficulty. Looks like that's an empty string in the TMX API although it's definitely being used on TMX itself.
  - Get the map's assigned tags. Also seems to be an empty string. There is a `StyleName` property that seems to contain the first tag.
  - Use an embed instead of a standard message (see https://discord.com/developers/docs/resources/channel#embed-object).
- Bot functionality:
  - Make the bot listen to a command for adding/removing channels to the post list (needs to be persisted).
  - Cache the current TOTD (or its message) so we only need to make the request once.
  - Post the TOTD message on a schedule.
  - Add a command to manually post the current TOTD message (maybe without the reactions?).
