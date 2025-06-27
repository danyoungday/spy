from dataclasses import dataclass
import json
import re

from agents.player import Player, NotSpy, Spy

@dataclass
class Config:
    model_name: str = "gpt-4o"
    player_temperature: float = 1.0
    num_players: int = 6
    location: str = "Pirate Ship"


def get_current_history_idx(chat_history: list[dict[str, str]], next_id: int) -> int:
    """
    Goes through the chat history backwards and returns the index of the last message sent by the player with next_id.
    If no message is found, returns -1.
    """
    for idx in range(len(chat_history) - 1, -1, -1):
        if chat_history[idx]["player_id"] == next_id:
            return idx
    return -1


def parse_response(response: str) -> dict:
    """
    Parses the agent's response from a string to a dict.
    """
    json_str = re.search(r'\{.*\}', response, re.DOTALL).group()
    formatted_msg = json.loads(json_str)
    return formatted_msg


def query_player(players: list[Player],
                 player_id: int,
                 chat_history: list[dict[str, str]]) -> dict[str, str]:
    """
    Queries a player based on the chat history and returns their response.
    """
    player = players[player_id - 1]
    relevant_history = chat_history[get_current_history_idx(chat_history, player_id) + 1:]
    msg = player.get_response_multi(relevant_history)
    response_dict = parse_response(msg)
    return response_dict


def main():
    config = Config()
    players = [NotSpy(config, player_id=i+1) for i in range(config.num_players-1)] + [Spy(config, player_id=config.num_players)]
    next_id = 1
    chat_history = [{"player_id": -1, "message": "Player 1, begin the game by choosing another player and asking them a question."}]
    for i in range(20):
        print("-----------")
        print(next_id)
        response_dict = query_player(players, next_id, chat_history)
        print(json.dumps(response_dict, indent=2))
        chat_history.append({"player_id": next_id, "message": f"{response_dict['message']}"})
        next_id = int(response_dict["next"])

    chat_history.append({})
    for i in range(1, config.num_players):
        chat_history[-1] = {"player_id": -1, "message": f"Player {i}, who do you think is the spy and why? Make your best guess."}
        response_dict = query_player(players, i, chat_history)
        print(json.dumps(response_dict, indent=2))

    chat_history[-1] = {"player_id": -1, "message": f"Player {config.num_players}, what location are we in? Make your best guess."}
    response_dict = query_player(players, config.num_players, chat_history)
    print(json.dumps(response_dict, indent=2))


if __name__ == "__main__":
    main()
