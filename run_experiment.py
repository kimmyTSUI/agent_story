"""
海龟汤游戏实验运行脚本
支持使用OpenAI API、Anthropic API或其他LLM服务
"""

import json
import os
from typing import Dict, Callable
from game_controller import TurtleSoupGame
from evaluator import GameEvaluator


def load_puzzle_data(json_path: str, puzzle_index: int = 0) -> Dict:
    """
    从JSON文件加载谜题数据

    Args:
        json_path: JSON文件路径
        puzzle_index: 谜题索引（默认为0，即第一个谜题）

    Returns:
        谜题数据字典
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if puzzle_index >= len(data):
        raise ValueError(f"谜题索引 {puzzle_index} 超出范围（共有 {len(data)} 个谜题）")

    return data[puzzle_index]


def create_openai_api_call(api_key: str = None, model: str = "gpt-4") -> Callable:
    """
    创建OpenAI API调用函数

    Args:
        api_key: OpenAI API密钥（如果不提供，会从环境变量OPENAI_API_KEY读取）
        model: 模型名称

    Returns:
        API调用函数
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("请先安装OpenAI库: pip install openai")

    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请提供OpenAI API密钥或设置环境变量OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)

    def api_call(system_prompt: str, user_prompt: str) -> str:
        """调用OpenAI API"""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

    return api_call


def create_anthropic_api_call(api_key: str = None, model: str = "claude-3-5-sonnet-20241022") -> Callable:
    """
    创建Anthropic API调用函数

    Args:
        api_key: Anthropic API密钥（如果不提供，会从环境变量ANTHROPIC_API_KEY读取）
        model: 模型名称

    Returns:
        API调用函数
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError("请先安装Anthropic库: pip install anthropic")

    if api_key is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("请提供Anthropic API密钥或设置环境变量ANTHROPIC_API_KEY")

    client = Anthropic(api_key=api_key)

    def api_call(system_prompt: str, user_prompt: str) -> str:
        """调用Anthropic API"""
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.content[0].text

    return api_call


def create_mock_api_call() -> Callable:
    """
    创建模拟API调用函数（用于测试，不调用真实API）

    Returns:
        模拟API调用函数
    """
    call_count = [0]  # 使用列表来保持可变性

    def mock_call(system_prompt: str, user_prompt: str) -> str:
        """模拟API调用"""
        call_count[0] += 1

        # 根据提示内容返回不同的模拟响应
        if "主持人" in system_prompt:
            # 模拟主持人回答
            responses = ["是。", "否。", "不重要。"]
            return responses[call_count[0] % 3]
        elif "玩家" in system_prompt:
            # 模拟玩家提问
            if "最终推理" in user_prompt:
                return "[最终推理] 这个人假装自己死了，实际上逃到了一个偏远的岛屿，后来给家人寄了一封信。"
            else:
                questions = [
                    "[提问] 这个人真的死了吗？",
                    "[提问] 他是故意假死的吗？",
                    "[提问] 他去了一个偏远的地方吗？",
                    "[提问] 他有什么目的吗？"
                ]
                return questions[call_count[0] % len(questions)]
        else:
            # 其他情况（如评估）
            return "核心情节：7/10\n关键细节：6/10\n逻辑推理：8/10\n整体完整度：7/10\n总体评分：70/100"

    return mock_call


def run_single_game(
    puzzle_data: Dict,
    model_api_call: Callable,
    max_rounds: int = 20,
    players_config: list = None,
    save_log: bool = True,
    log_path: str = None
) -> Dict:
    """
    运行单个游戏

    Args:
        puzzle_data: 谜题数据
        model_api_call: LLM API调用函数
        max_rounds: 最大回合数
        players_config: 玩家配置
        save_log: 是否保存游戏日志
        log_path: 日志保存路径

    Returns:
        游戏日志（包含评估结果）
    """
    # 创建游戏
    game = TurtleSoupGame(
        puzzle_data=puzzle_data,
        model_api_call=model_api_call,
        max_rounds=max_rounds,
        players_config=players_config
    )

    # 运行游戏
    game_log = game.run_game()

    # 评估游戏
    evaluator = GameEvaluator(game_log, model_api_call)
    evaluator.evaluate_all()
    evaluator.print_detailed_report()

    # 保存日志
    if save_log:
        if log_path is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = f"game_log_{timestamp}.json"

        game.save_game_log(log_path)

    return game_log


def main():
    """
    主函数 - 运行实验
    """
    print("="*60)
    print("海龟汤游戏 - Agent推理实验")
    print("="*60)

    # 1. 加载谜题数据
    print("\n加载谜题数据...")
    puzzle_data = load_puzzle_data("test.json", puzzle_index=0)
    print(f"已加载谜题 #{puzzle_data.get('index', 0)}")

    # 2. 选择API
    print("\n选择LLM API:")
    print("1. OpenAI (需要设置OPENAI_API_KEY)")
    print("2. Anthropic (需要设置ANTHROPIC_API_KEY)")
    print("3. Mock API (测试模式，不调用真实API)")

    choice = input("\n请选择 (1/2/3): ").strip()

    if choice == "1":
        print("\n使用OpenAI API...")
        model_api_call = create_openai_api_call()
    elif choice == "2":
        print("\n使用Anthropic API...")
        model_api_call = create_anthropic_api_call()
    else:
        print("\n使用Mock API (测试模式)...")
        model_api_call = create_mock_api_call()

    # 3. 配置游戏参数
    players_config = [
        {"name": "Player1", "strategy": "systematic"},
        {"name": "Player2", "strategy": "creative"}
    ]
    max_rounds = 20

    # 4. 运行游戏
    print("\n" + "="*60)
    print("开始游戏...")
    print("="*60)

    game_log = run_single_game(
        puzzle_data=puzzle_data,
        model_api_call=model_api_call,
        max_rounds=max_rounds,
        players_config=players_config,
        save_log=True
    )

    print("\n" + "="*60)
    print("实验完成！")
    print("="*60)


if __name__ == "__main__":
    main()
