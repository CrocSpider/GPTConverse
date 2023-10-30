
# Voice-Activated Chatbot

This project implements a voice-activated chatbot using OpenAI's ChatGPT-4 for generating responses, ElevenLabs for voice synthesis, Whisper for speech recognition, and WebRTC VAD for voice activity detection.

## Features

- Voice input and output
- Continuous conversation flow
- Uses ChatGPT-4 for generating responses
- ElevenLabs for turning text responses into voice
- Whisper for transcribing voice input
- Voice activity detection for dynamic response lengths

## Installation

1. Clone this repository:

    git clone [https://github.comCrocSpider/GPTConverse.git](https://github.com/CrocSpider/GPTConverse.git)

2. Navigate to the project directory:

    cd your-repo-name

3. Install the required Python packages:

    pip install -r requirements.txt


## Setup

Before running the application, you need to set up the following environment variables with your API keys:

- `OPENAI_API_KEY`: Your OpenAI API key for accessing ChatGPT-4.
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key for voice synthesis.

You can set these variables in your environment or add them to a `.env` file in the project root (if using a library like `python-dotenv` for environment management).

## Usage

To run the chatbot, execute:

    python app.py


Start speaking after prompted, and the chatbot will respond with a voice output.

## License

[MIT](LICENSE)

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/yourusername/your-repo-name/issues) if you want to contribute.

## Author

- Ding
