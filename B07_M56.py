# B07_M56.py
import logging

class M56:
    # Initialize a M56 instance.
    def __init__(self, system_message, messages_per_channel):
        # Create a messages dictionary
        self.messages_by_channel = {}
        self.system_message = system_message
        self.messages_per_channel = messages_per_channel
    """
    This class represents a Message manager, providing functionalities related to conversations. 
    """

    def add_to_messages(self, channel, nickname, message, role):
        if channel not in self.messages_by_channel:
           # Init a new channel with the `system_message` set in yaml config.
           self.messages_by_channel[channel] = []
           self.messages_by_channel[channel].extend([{"role": "system", "content": self.system_message}])
        if role == "assistant" or role == "system":
            self.messages_by_channel[channel].append({
                "role": role,
                "content": f"{message}"
            })
        elif role == "user":
            self.messages_by_channel[channel].append({
                "role": "user",
                "content": f'{nickname} says, "{message}"'
            })
        # Keep a number of total system+assistant+user messages per channel
        #   `messages_per_channel` set in yaml config.
        if len(self.messages_by_channel[channel]) > self.messages_per_channel:
            self.messages_by_channel[channel].pop(1)
        return self.messages_by_channel[channel]