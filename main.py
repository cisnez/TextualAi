# B07_C0R3.py

# Bot name used in various places.
import sys
bot_name = sys.argv[1].lower()

# Set logging.DEBUG to see ALL logs; set logging.INFO for less
import logging
logging.basicConfig(level=logging.INFO, filename=f'{bot_name}.log', filemode='w')

# Create a yaml object
from B07_Y4ML import Y4ML
yaml = Y4ML()

# Define all the required YAML files to initialize Discord Bot.
config_files = [f"_init_{bot_name}.yaml", "_init__global.yaml"]
# Merge the files using a B07_Y4ML.py method.
bot_init_data = yaml.merge_files(config_files)

# Get key and token from the OS environment
import os
xai_api_key = os.getenv("XAI_API_KEY")
bot_discord_token = os.environ.get(f'{bot_name.upper()}_TOKEN')

# Create xAI API Client
from openai import OpenAI
xai_client = OpenAI(
    api_key=xai_api_key,
    base_url=bot_init_data["llm_url"],
)
    
# Create a messages object
from B07_M56 import M56
msgs = M56(xai_client, bot_init_data["system_message"], bot_init_data["messages_per_channel"], bot_name)

from B07_C0R3 import D15C0R6
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Pretty, TextArea, Button, Footer, Header
import asyncio

class Discord_Bot(HorizontalGroup):

    # Init placeholder for asyncio task
    bot_task = None

    # Create a new bot object using the merged YAML init files...
    # and the D15C0R6 constructor class from B07_C0R3.py
    bot = D15C0R6(bot_discord_token, bot_init_data, bot_name, msgs)

    def compose(self) -> ComposeResult:
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button(f"{bot_name.capitalize()}", id="bot_name")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start":
            # Create the run_bot asyncio task
            self.bot_task = asyncio.create_task(self.run_bot(self.bot))
            self.add_class("started")
            logging.info(f"{bot_name}: Created new asyncio bot_task.")
        elif event.button.id == "stop":
            self.stop_bot()
            self.remove_class("started")
            logging.info(f"{bot_name}: Stopped asyncio bot_task.")

    # Coroutine to run a bot instance
    async def run_bot(self, bot):
        await bot.start(bot.discord_token)

    async def stop_bot(self):
        while not self.bot_task.done():
            await self.bot.close()
            await asyncio.sleep(2)
        await self.bot_task.cancel()

class Pretty_Init(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Pretty(bot_init_data)

class TextualAi(App):
    """A Textual app to manage Discord bot using OpenAI API."""

    CSS_PATH = "main.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Discord_Bot()
        yield VerticalScroll(Pretty_Init())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    app = TextualAi()
    app.run()
