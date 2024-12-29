# B07_C0R3.py

# Bot name used in various places.
import sys
bot_name = sys.argv[1].lower()

# Set logging.DEBUG to see ALL logs; set logging.INFO for less
import logging
logging.basicConfig(filename=f'main~{bot_name}.log', filemode='w', level=logging.INFO)

import os
import asyncio
from openai import OpenAI
from B07_C0R3 import D15C0R6
from B07_Y4ML import Y4ML
from B07_M56 import M56
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Footer, Header

# Create a yaml object
yaml = Y4ML()

# Define all the required YAML files to initialize Discord Bot.
config_files = ["_init__global.yaml", f"_init_{bot_name}.yaml"]
# Merge the files using a B07_Y4ML.py method.
bot_init_data = yaml.merge_files(config_files)

# Get key and token from the OS environment
xai_api_key = os.getenv("XAI_API_KEY")
bot_discord_token = os.environ.get(f'{bot_name.upper()}_TOKEN')

# Create xAI API Client
xai_client = OpenAI(
    api_key=xai_api_key,
    base_url="https://api.x.ai/v1",
)
    
# Create a messages object
msgs = M56(bot_init_data["system_message"])

class Discord_Bot(HorizontalGroup):

    # Init placeholder for asyncio task
    bot_task = None

    # Create a new bot object using the merged YAML init files...
    # and the D15C0R6 constructor class from B07_C0R3.py
    bot = D15C0R6(xai_client, bot_discord_token, bot_init_data, bot_name, msgs)

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

class xAI_Discord_App(App):
    """A Textual app to manage Discord bot using OpenAI API."""

    CSS_PATH = "main.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Discord_Bot())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    app = xAI_Discord_App()
    app.run()
