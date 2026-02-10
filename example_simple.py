"""
简单示例：快速运行一个海龟汤游戏
这个脚本展示了如何使用框架的最小示例
"""

import json
from game_controller import TurtleSoupGame
from evaluator import GameEvaluator


def simple_mock_api(system_prompt: str, user_prompt: str) -> str:
    """
    简单的模拟API函数，用于演示
    实际使用时应该替换为真实的LLM API调用
    """
    # 这里只是返回固定响应，实际应该调用真实API
    if "主持人" in system_prompt:
        if "假死" in user_prompt or "fake" in user_prompt.lower():
            return "是。"
        elif "犯罪" in user_prompt or "illegal" in user_prompt.lower():
            return "是。"
        else:
            return "不相关。"
    elif "最终推理" in user_prompt:
        return "[最终推理] 基于对话，我认为这个人假装自己死了，可能是为了逃避某些麻烦，然后躲到了一个偏远的岛屿，后来给家人寄了信报平安。"
    else:
        # 玩家提问
        return "[提问] 这个人是故意假死的吗？"


def main():
    # 1. 加载谜题数据
    with open("test.json", 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    puzzle_data = puzzles[0]  # 使用第一个谜题

    # 2. 配置玩家
    players_config = [
        {"name": "探索者", "strategy": "systematic"},
        {"name": "直觉派", "strategy": "creative"}
    ]

    # 3. 创建并运行游戏
    game = TurtleSoupGame(
        puzzle_data=puzzle_data,
        model_api_call=simple_mock_api,
        max_rounds=25,
        players_config=players_config
    )

    game_log = game.run_game()

    # 4. 评估
    evaluator = GameEvaluator(game_log, simple_mock_api)
    evaluator.evaluate_all()
    evaluator.print_detailed_report()

    # 5. 保存结果
    game.save_game_log("example_game_log.json")


if __name__ == "__main__":
    main()
