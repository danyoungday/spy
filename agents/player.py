from agents.agent import Agent


class Player:
    def __init__(self, config, system_prompt: str, player_id: int):
        self.player_id = player_id
        self.agent = Agent(model=config.model_name,
                           system_prompt=system_prompt,
                           temperature=config.player_temperature)

    def get_response_multi(self, new_chats: list[dict[str, str]]) -> str:
        """
        Takes in chat history in the format:
        [
            {"player_id": 1, "message": "Player 2, what is the temperature here?"},
            {"player_id": 2, "message": "I think the temperature is quite warm. Player 3, ..."},    
        ]
        """
        chat_history = []
        for chat in new_chats:
            player = f"Player {chat['player_id']}" if chat['player_id'] > 0 else "Administrator"
            chat_history.append(f"{player}: {chat['message']}")
        chat_history_str = "\n".join(chat_history)
        return self.agent.get_response(chat_history_str)


class NotSpy(Player):
    def __init__(self, config, player_id: int):
        with open("spyfall_prompt.txt", "r") as f:
            spyfall_prompt = f.read()

        system_prompt = f"""{spyfall_prompt}
You are player id: {player_id} out of {config.num_players} players.
You are not the spy and have received the following location card: {config.location}.
On your turn always do these two things:
    1. If you were asked a question, you must respond to it and do so in a way that does not reveal the location to the spy, but also would not make you seem suspicious to the other non-spy players.
    2. Ask a question to another player to gather information on whether they are the spy. Make sure your question does not reveal the location to the spy.
Format your response in json format exactly as follows:
    {{
        "thinking": <Your thought process here>",
        "message": <Your public message which includes your response to the question asked to you and your question to the next player. Note: all other players will see this message>,
        "next": <The player ID of the player you want to ask your question to. Only use a number from 1 to {config.num_players}, do not say "Player" before>
    }}
"""
        super().__init__(config, system_prompt, player_id)


class Spy(Player):
    def __init__(self, config, player_id: int):
        with open("spyfall_prompt.txt", "r") as f:
            spyfall_prompt = f.read()

        system_prompt = f"""{spyfall_prompt}
You are player id: {player_id} out of {config.num_players} players.
You are the spy and do not know the location.
On your turn always do these two things:
    1. If you were asked a question, you must respond to it and do so in a way that does not make you suspicious to the other non-spy players.
    2. Ask a question to another player to gather information on the location. Make sure your question does not reveal yourself as the spy.
Format your response in json format exactly as follows:
    {{
        "thinking": <Your thought process here>",
        "message": <Your public message which includes your response to the question asked to you and your question to the next player. Note: all other players will see this message>,
        "next": <The player ID of the player you want to ask your question to. Only use a number from 1 to {config.num_players}, do not say "Player" before>
    }}
"""
        super().__init__(config, system_prompt, player_id)
