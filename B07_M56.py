# B07_M56.py
import logging

class M56:
    # Initialize a M56 instance.
    def __init__(self, system_message, messages_per_channel):
        # Create a messages dictionary
        self.messages_by_channel = {}
        self.system_message = [{"role": "system", "content": system_message}]
        self.messages_per_channel = messages_per_channel
    """
    This class represents a Message manager, providing functionalities related to conversations. 
    """

    def add_to_messages(self, channel, nickname, message, role):
        if channel not in self.messages_by_channel:
           self.messages_by_channel[channel] = []
           self.messages_by_channel[channel].extend(self.system_message)
        if role == "assistant":
            self.messages_by_channel[channel].append({
                "role": "assistant",
                "content": f"{message}"
            })
        elif role == "user":
            self.messages_by_channel[channel].append({
                "role": "user",
                "content": f'{nickname} says, "{message}"'
            })
        if len(self.messages_by_channel[channel]) > self.messages_per_channel:  # Keep 7 messages for example
            self.messages_by_channel[channel].pop(1)
        return self.messages_by_channel[channel]