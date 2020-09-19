# Trackmania TOTD Discord Bot

## Setup

### Configuration

Using `.env.template`, create a file called `.env` and fill in your credentials. This is required for the bot to run.

## Ideas for Improvements

- Show the map's thumbnail. The URL is contained in the map information.
- Get the TMX information if available: We can use the [TMX API](https://api.mania-exchange.com/documents/reference#information) to get map information by its in-game mapUid.
  - Get the TMX thumbnail. Typically, maps on TMX have a stylized thumbnail that's better than the in-game one.
  - Get the map's assigned difficulty. Looks like that's an empty string in the TMX API although it's definitely being used on TMX itself.
  - Get the map's assigned tags. Also seems to be an empty string. There is a `StyleName` property that seems to contain the first tag.
- Show the author's name. TMX has the TMX username, but that might be different from the in-game one. We might be able to get the in-game one using [the v3/profiles route](https://github.com/The-Firexx/trackmania2020apidocumentation/blob/master/UbiServices.md#get-v3profiles).

An example of a map's TMX data: [Edinburgh (Uid: "ia2DTzgOoCl6hPiThc657ssJPV")](https://trackmania.exchange/api/tracks/get_track_info/multi/ia2DTzgOoCl6hPiThc657ssJPV).
