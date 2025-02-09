# TextualGrok
Textual interface for xAI Grok chatbot for Discord.

## Description
A Python based Discord bot using `Discord API` and xAI Grok `OpenAI API` to provide conversational functionality.

## Files
- main.py
- main.tcss
- B07_C0R3.py
- B07_Y4ML.py
- _init_botname.yaml
- _init__global.yaml

## Usage
1. Clone the repository to your local machine.
2. Configure your bot by modifying the example `_init_botname.yaml` template.
3. Create a system environment variable for your bot's XAI_API_KEY
4. Create a system environment variable for your bot's DISCORD_TOKEN
5. Install requirements. `pip install -r requirements.txt`
6. Run the bot using `python main.py botname`.
7. Check the new log file `main~botname.log`. Debug logs available, change to `level=logging.DEBUG` in `main.py`.