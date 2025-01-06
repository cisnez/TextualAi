# B07_C0R3.py
import logging
import asyncio
from discord.ext import commands as commANDs
from discord import Intents as InTeNTs
from discord import utils as UtIls

class D15C0R6(commANDs.Bot):
    def __init__(self, xai_client, discord_token, bot_init_data, bot_name, msgs):
        self.name = bot_name
        self.xai_client = xai_client
        self.msgs = msgs
        self.response_tokens = bot_init_data["response_tokens"]
        self.discord_token = discord_token
        self.command_prefix = bot_init_data["command_prefix"]
        # Assign all yaml values within the __init__ method
        self.home_channel_id = bot_init_data["home_channel_id"]
        self.ignored_prefixes = bot_init_data["ignored_prefixes"]
        self.llm_model = bot_init_data["llm_model"]
        self.specifity_creativity = bot_init_data["specifity_creativity"]
        # A set ensures that these collections only store unique elements
        self.allow_author_ids = set(bot_init_data["allow_author_ids"])
        self.allow_channel_ids = set(bot_init_data["allow_channel_ids"])
        self.ignore_author_ids = set(bot_init_data["ignore_author_ids"])
        self.ignore_channel_ids = set(bot_init_data["ignore_channel_ids"])
        # Parent class assignments for: super().__init__()
        in_tents = InTeNTs(**bot_init_data["intents"])
        super().__init__(command_prefix=self.command_prefix, intents=in_tents)

    async def close(self):
        await super().close()
    
    async def on_connect(self):
        logging.info(f"{self.user} has connected to Discord.")

    async def on_disconnect(self):
        logging.info(f"{self.user} has disconnected from Discord.")

    async def on_ready(self):
        logging.info(f"{self.user} ready to receive commands. ID: {self.user.id}")

    async def on_resumed(self):
        logging.info(f"{self.user} has reconnected to Discord; ready to receive commands.")

    async def on_member_remove(self, member):
        channel = self.get_channel(self.home_channel_id)
        nickname = member.nick if member.nick is not None else member.display_name
        await channel.send(f":wave: {nickname} has left the server.\nID: {member.id}\nName: {member.name}")
        logging.info(f"{nickname} has left the server.")

    async def on_member_join(self, member):
        channel = self.get_channel(self.home_channel_id)
        nickname = member.nick if member.nick is not None else member.display_name
        await channel.send(f":cake: {nickname} has joined the server.\nID: {member.id}\nName: {member.name}")
        logging.info(f"{nickname} has joined the server.")

    async def on_user_update(self, before, after):
        channel = self.get_channel(self.home_channel_id)
        avatar_changed = "**Yes**" if before.avatar != after.avatar else "**No**"
        if before.name == after.name and before.display_name == after.display_name:
            await channel.send(f":bangbang: **User profile updated.** :bangbang:\nUser:{after.name}\nDisplay Name:{after.display_name}\nAvatar Changed? [{avatar_changed}]")
        else:
            await channel.send(f":bangbang: **User profile updated.** :bangbang:\nBefore: ```User:{before.name}\nDisplay Name:{before.display_name}```After: ```User:{after.name}\nDisplay Name:{after.display_name}```Avatar Changed? [{avatar_changed}]")
        logging.info(f"User {before} has updated their profile. {after}")

    # If you define an on_message event, the bot will not process commands automatically unless you explicitly call `await self.process_commands(message)`. This is because the `on_message`` event is processed before the command, so if you don't call `process_commands`, the command processing stops at `on_message`.
    async def on_message(self, message):
        nickname = message.author.nick if message.author.nick is not None else message.author.display_name
        logging.debug(f'\n-- BEGIN ON_MESSAGE FROM `{nickname}` --')
        
        if "<|separator|>" in message.content:
            # In case LLM returns nothing the API returns `<|seperator|>`, which throws an exception error.
            logging.info("<|separator|> violation found in message.")

        elif message.author.id == self.user.id:
            self.msgs.add_to_messages(message.channel.id, self.name, message.content, "assistant")
            logging.debug(f'{self.name}: Added message with assistant role.')

        elif message.channel.id in self.ignore_channel_ids:
            logging.debug(f'Ignored Channel ID: {message.channel.name}\n')

        elif message.author.id in self.ignore_author_ids:
            self.msgs.add_to_messages(message.channel.id, nickname, message.content, "user")
            self.msgs.add_to_messages(message.channel.id, "system", f"Ignored message from {nickname}", "system")
            logging.debug(f'Ignoring Author: {nickname}')

        elif message.content.startswith('.delete') and (message.author.id in self.allow_author_ids):
            if message.reference:  # Check if the message is a reply
                try:
                    referenced_message = await message.channel.fetch_message(message.reference.message_id)
                    if referenced_message.author.id == self.user.id:
                        self.msgs.add_to_messages(message.channel.id, nickname, f"Delete your message with ID: {referenced_message.id}", "user")
                        await referenced_message.delete()
                        self.msgs.add_to_messages(message.channel.id, self.name, f"Deleted my message as requested by {nickname}", "system")
                        logging.info(f"Deleted message from self, ID: {referenced_message.author.id}.")
                    else:
                        logging.debug(f"Delete request for message by other user ID: {referenced_message.author.id}.")
                except Exception as e:
                    await message.channel.send(f"Error deleting message: {e}")
                    logging.error(f"Error deleting message: {e}")
                await message.delete()  # Delete the command message if allowed
                logging.debug(f"Attempted to delete command message from: {message.author.id}.")
        
        elif message.content.startswith('.hello'):
            reply = "Hello Channel!"
            self.msgs.add_to_messages(message.channel.id, nickname, reply, "user")
            await message.channel.send(reply)
            logging.debug(f'{self.name}: `.hello` command received.')

        elif message.content.startswith('.shutdown') and (message.author.id in self.allow_author_ids):
            await message.channel.send("Shutting down...")
            logging.info('.shutdown command received.')
            await self.close()
        
        elif any(message.content.startswith(prefix) for prefix in self.ignored_prefixes):
            logging.debug(self.ignored_prefixes)
            for prefix in self.ignored_prefixes:
                if message.content.startswith(prefix):
                    logging.debug(f'Ignoring message due to prefix: {prefix}\n')

        elif message.author.id in self.allow_author_ids or message.channel.id in self.allow_channel_ids:
            logging.debug(f"\nMessage from {message.author.name} received:\n{message.content}\n")
            # The bot will show as typing while executing the code inside this block
            # So place your logic that takes time inside this block
            async with message.channel.typing():
                # Remove bot's mention from the message
                clean_message = UtIls.remove_markdown(str(self.user.mention))
                prompt_without_mention = message.content.replace(clean_message, "").strip()
                messages = self.msgs.add_to_messages(message.channel.id, nickname, prompt_without_mention, "user")
                # Add context to the prompt
                logging.debug(f"\nSending usr_prompt to Grok\n{messages}\n")
                response_text = self.get_response(messages, self.llm_model, self.response_tokens, 1, self.specifity_creativity)
                if response_text:
                    # Add response text to messages at start of on_message()
                    await message.channel.send(response_text)
                    logging.debug(f"\nMessage history:\n{self.msgs.messages_by_channel[message.channel.id]}\n")
                else:
                    logging.error("No response from get_response")

        else:
            if (message.author.id != self.user.id):
                self.msgs.add_to_messages(message.channel.id, nickname, message.content, "user")
                messages = self.msgs.add_to_messages(message.channel.id, nickname, f"Ignored message from: {nickname}", "system")

                logging.debug('message from else')
                logging.debug(f'-----\n`message.author.name`: `{message.author.name}`\n`message.channel.id`: `{message.channel.id}`,\n`message.channel.name`: `{message.channel.name}`,\n`message.id`: `{message.id}`,\n`message.author.id`: `{message.author.id}`\n')
            else:
                logging.debug('message from self . . . how did the code even get here !?')
                logging.debug(f'-----\n`message.author.name`: `{message.author.name}`\n`message.channel.id`: `{message.channel.id}`,\n`message.channel.name`: `{message.channel.name}`,\n`message.id`: `{message.id}`,\n`message.author.id`: `{message.author.id}`\n')
        # Always process commands at the end of the on_message event
        await self.process_commands(message)
        logging.debug(f'\n-- END ON_MESSAGE FROM `{nickname}` --\n')

    def get_response(self, messages, model, max_response_tokens, n_responses, specifity_creativity):
        try:
            completions = self.xai_client.chat.completions.create(
                # "grok-beta" set in the init file
                model=model,
                # messages=[
                #     {"role": "system", "content": sys_prompt},
                #     {"role": "user", "content": usr_prompt},
                # ],
                messages = messages,  # from build_messages method
                max_tokens = max_response_tokens,
                n=n_responses,
                stop=None,
                # specifity < 0.5 > creativity
                temperature=specifity_creativity,
            )
            response = completions.choices[0].message.content
            return response
        except Exception as e:
            exception_error = (f"Error in get_response: {e}")
            logging.error(exception_error)
            return exception_error
