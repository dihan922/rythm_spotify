# Fake Ah Rythm

A nostalgic clone of the well-known Discord music bot, Rythm. This bot simulates the behavior of Rythm by utilizing Spotify for music playback.

## Disclaimer

This project is a rudimentary alternative for nostalgic purposes. It directly affects your Spotify playback, and the audio can be routed to a Discord channel using a virtual audio cable. Please note that this is not a perfect replacement for the original Rythm bot.

## Acknowledgments

This project is inspired by the original Rythm bot, which is now defunct. Credits to the Rythm team for their contributions to the Discord music bot community.

## Getting Started

Follow these instructions to get the Fake Ah Rythm bot up and running for your Discord server.

### Prerequisites

1. **Spotify Developer App:**
   - Create a Spotify Developer App: [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
   - Note down your Client ID and Client Secret.

2. **Discord Developer App**
    - Create a Discord Developer App: [Discord Developer Portal](https://discord.com/developers/applications)
    - Note down your Bot Token.
    - Generate an OAuth2 URL for your bot and invite it to your server.

3. **Python and Pip:**
   - Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).
   - Install `pip` if you haven't already.

4. **Clone the Repository:**
   ```bash
   git clone https://github.com/dihan922/fake_ah_rythm
   cd Fake_Ah_Rythm
   ```

### Dependencies

1. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2. **Add your Discord and Spotify API credentials in credentials.py:**
    ```py
    SPOTIPY_CLIENT_ID = your_spotify_client_id
    SPOTIPY_CLIENT_SECRET = your_spotify_client_secret
    DISCORD_TOKEN = your_discord_bot_token
    ```

## Usage

1. **Run the bot:**
    ```bash
    python bot.py
    ```

2. **Play this [playlist](https://open.spotify.com/playlist/4JqQJIevpZoz10eRFTM7pR?si=d34db9c791814d3e) on Spotify to simulate an empty song queue.**
   - Note: Bot will work without playlist, but info about remaining time until song plays will be missing.

3. **Use the commands to interact with the bot and control your Spotify playback.**

### Commands

- `&play <song>` or `&p <song>`: Play a song from Spotify.
- `&skip`: Skip to the next track.
- `&previous`: Skip back to the previous track.
- `&pause`: Pause the playback.
- `&resume`: Resume the playback.
- `&nowplaying` or `&np`: Display the currently playing song.
- `&seek <timestamp>`: Set the playback position to a specified timestamp.
- `&queue` or `&q`: Display the queue.

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit).
