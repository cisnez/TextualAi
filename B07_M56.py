# B07_M56.py
import logging
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

# Initialize Sentence-Transformers model
transformer_model = SentenceTransformer('all-MiniLM-L6-v2')

class M56:
    # Initialize a M56 instance.
    def __init__(self, xai_client, system_message, messages_per_channel):
        self.xai_client = xai_client
        # Create a messages dictionary
        self.messages_by_channel = {}
        self.system_message = system_message
        self.messages_per_channel = messages_per_channel
        self.embedding_function = EmbeddingFunction()
        self.chroma_client = chromadb.PersistentClient(path="./chromadb_data")
        self.collection = self.chroma_client.get_or_create_collection(name="conversations", embedding_function=self.embedding_function)
    """
    This class represents a Message manager, providing functionalities related to conversations. 
    """

    def add_to_messages(self, channel_id, nickname, message, role):
        if channel_id not in self.messages_by_channel:
           # Init a new channel with the `system_message` set in yaml config.
           self.messages_by_channel[channel_id] = []
           self.messages_by_channel[channel_id].extend([{"role": "system", "content": self.system_message}])
        if role == "assistant" or role == "system":
            self.messages_by_channel[channel_id].append({
                "role": role,
                "content": f"{message}"
            })
        elif role == "user":
            self.messages_by_channel[channel_id].append({
                "role": role,
                "content": f'{nickname} says, "{message}"'
            })
            
        # Add message to ChromaDB
        add_timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.collection.add(documents=[message], ids=[add_timestamp],
                metadatas=[{"role": role, "channel_id": channel_id, "nickname": nickname}]
        )
        
        # Keep a number of total system+assistant+user messages per channel
        #   `messages_per_channel` set in yaml config.
        if len(self.messages_by_channel[channel_id]) > self.messages_per_channel:
            self.messages_by_channel[channel_id].pop(1)

        return self.messages_by_channel[channel_id]
        
    def get_messages(self, channel_id, message):
        query_results = collection.query(
            query_texts=context_response.content,
            where={"role": "assistant", "channel_id": channel_id},
            n_results=3
        )
        return query_results
    
    def respond_to_user(self, channel_id, nickname, message, model, max_response_tokens, specifity_creativity):
        
        messages = []
        
        # Get the context of the message.
        context=[
            {"role": "system", "content": "Return <=5 keywords as CSV."},
            {"role": "user", "content": message}
            ]
        context_response = self.get_llm_response(context, model, max_response_tokens, 1, 0.42)
        logging.info(f"Context:\n{context_response}")
        
        # Query saved messages with the context response
        query_results = self.collection.query(
            query_texts=context_response,
            where={"role": "assistant"},
            n_results=3
        )
        
        # Add system message and append the query result into the messages
        messages.extend([{"role": "system", "content": "Remember previous messages."}])
        for res in query_results['documents'][0]:
            messages.append({"role": "assistant", "content": f"{res}"})

        # Add latest message and context to ephemeral memory
        self.add_to_messages(channel_id, nickname, message, "user")
#        self.add_to_messages(channel_id, nickname, f"Context: {context_response}", "system")

        # Append ephemeral messages to messages
        messages.extend(self.messages_by_channel[channel_id])
        logging.info(f"Messages:\n{messages}")
        
        # Get response from LLM
        response_text = self.get_llm_response(messages, model, max_response_tokens, 2, specifity_creativity)
        
        return response_text

    def get_llm_response(self, messages, model, max_response_tokens, n_responses, specifity_creativity):
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
            exception_error = (f"Error in get_llm_response: {e}")
            logging.error(exception_error)
            return exception_error
        
class EmbeddingFunction:
    def __call__(self, input):
        return transformer_model.encode(input).tolist()
