"""
海龟汤游戏控制器
负责协调主持人和玩家之间的交互，管理游戏流程
"""

from typing import Dict, List, Callable, Optional
import json
from datetime import datetime
from agents import HostAgent, PlayerAgent


class TurtleSoupGame:
    """
    海龟汤游戏控制器
    """

    def __init__(
        self,
        puzzle_data: Dict,
        model_api_call: Callable,
        max_rounds: int = 25,
        players_config: Optional[List[Dict]] = None
    ):
        """
        初始化游戏

        Args:
            puzzle_data: 谜题数据（包含surface、bottom、key_question等）
            model_api_call: 调用LLM的函数，签名为 func(system_prompt, user_prompt) -> str
            max_rounds: 最大回合数
            players_config: 玩家配置，格式如 [{"name": "Player1", "strategy": "systematic"}, ...]
        """
        self.puzzle_data = puzzle_data
        self.model_api_call = model_api_call
        self.max_rounds = max_rounds

        # 初始化主持人
        self.host = HostAgent(puzzle_data)

        # 初始化玩家
        if players_config is None:
            players_config = [
                {"name": "Player1", "strategy": "systematic"},
                {"name": "Player2", "strategy": "creative"}
            ]
        self.players = [
            PlayerAgent(config["name"], config.get("strategy", "systematic"))
            for config in players_config
        ]

        # 游戏状态
        self.conversation_history = []
        self.current_round = 0
        self.game_log = {
            "puzzle_index": puzzle_data.get("index", 0),
            "surface": puzzle_data["surface"],
            "bottom": puzzle_data["bottom"],
            "key_questions": puzzle_data["key_question"],
            "players": players_config,
            "max_rounds": max_rounds,
            "start_time": datetime.now().isoformat(),
            "rounds": [],
            "final_guesses": {},
            "evaluation": {},
            "winner": None
        }

    def play_round(self, player_idx: int) -> Dict:
        """
        执行一个回合（一个玩家提问）

        Args:
            player_idx: 玩家索引

        Returns:
            回合信息字典
        """
        player = self.players[player_idx]

        # 玩家提问
        print(f"\n{'='*60}")
        print(f"回合 {self.current_round + 1} - {player.player_name} 的回合")
        print(f"{'='*60}")

        player_response = player.ask_question(
            self.puzzle_data["surface"],
            self.conversation_history,
            self.model_api_call
        )

        print(f"\n{player.player_name}: {player_response}")

        # 检查是否是推理而非提问
        is_guess = "[推理]" in player_response or "[最终推理]" in player_response

        if is_guess:
            # 玩家给出了推理，主持人判断是否正确
            host_answer = self.host.evaluate_guess(player_response, self.model_api_call)
            print(f"主持人: {host_answer}")
            round_info = {
                "round": self.current_round + 1,
                "player": player.player_name,
                "question": player_response,
                "answer": host_answer,
                "is_guess": True,
                "guess_correct": host_answer == "是"
            }
            self.conversation_history.append(round_info)
        else:
            # 主持人回答
            host_answer = self.host.answer_question(player_response, self.model_api_call)
            print(f"主持人: {host_answer}")

            round_info = {
                "round": self.current_round + 1,
                "player": player.player_name,
                "question": player_response,
                "answer": host_answer,
                "is_guess": False,
                "guess_correct": False
            }

            self.conversation_history.append(round_info)

        self.game_log["rounds"].append(round_info)
        self.current_round += 1

        return round_info

    def run_game(self) -> Dict:
        """
        运行完整游戏

        Returns:
            游戏日志
        """
        print(f"\n{'#'*60}")
        print("海龟汤游戏开始！")
        print(f"{'#'*60}")
        print(f"\n汤面：{self.puzzle_data['surface']}")
        print(f"\n玩家：{', '.join([p.player_name for p in self.players])}")
        print(f"最大回合数：{self.max_rounds}")

        # 游戏主循环
        player_idx = 0
        game_ended = False
        correct_guess = None

        while self.current_round < self.max_rounds and not game_ended:
            round_info = self.play_round(player_idx)

            # 检查是否有玩家给出了正确推理
            if round_info.get("is_guess", False):
                print(f"\n{self.players[player_idx].player_name} 给出了推理！")
                if round_info.get("guess_correct", False):
                    print(f"{self.players[player_idx].player_name} 猜中真相，游戏暂停！")
                    self.game_log["winner"] = self.players[player_idx].player_name
                    correct_guess = round_info.get("question")
                    game_ended = True
                    break

            # 轮换玩家
            player_idx = (player_idx + 1) % len(self.players)

        # 游戏结束，让所有玩家给出最终推理（若无人猜中）
        if not self.game_log["winner"]:
            print(f"\n{'#'*60}")
            print("游戏结束！请各位玩家给出最终推理")
            print(f"{'#'*60}")

            for player in self.players:
                final_guess = player.make_final_guess(
                    self.puzzle_data["surface"],
                    self.conversation_history,
                    self.model_api_call
                )
                print(f"\n{player.player_name} 的最终推理：")
                print(final_guess)
                self.game_log["final_guesses"][player.player_name] = final_guess
        else:
            winner = self.game_log["winner"]
            self.game_log["final_guesses"][winner] = correct_guess or "已在对局中猜中真相。"

        # 显示真相
        print(f"\n{'#'*60}")
        print("真相揭晓！")
        print(f"{'#'*60}")
        print(f"\n{self.puzzle_data['bottom']}")

        # 记录结束时间
        self.game_log["end_time"] = datetime.now().isoformat()
        self.game_log["total_rounds"] = self.current_round

        return self.game_log

    def save_game_log(self, filepath: str):
        """
        保存游戏日志到文件

        Args:
            filepath: 保存路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.game_log, f, ensure_ascii=False, indent=2)
        print(f"\n游戏日志已保存到: {filepath}")
