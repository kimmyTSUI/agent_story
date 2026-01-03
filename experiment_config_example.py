"""
实验配置示例
展示如何进行各种类型的实验
"""

import json
from game_controller import TurtleSoupGame
from evaluator import GameEvaluator
from run_experiment import create_openai_api_call, create_anthropic_api_call, create_mock_api_call


# =============================================================================
# 实验1: 对比不同模型在同一谜题上的表现
# =============================================================================
def experiment_compare_models():
    """对比GPT-4和Claude在同一谜题上的表现"""
    with open("test.json", 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    puzzle = puzzles[0]

    # 配置相同的玩家设置
    players = [
        {"name": "Player1", "strategy": "systematic"},
        {"name": "Player2", "strategy": "creative"}
    ]

    # 测试GPT-4
    print("=" * 60)
    print("实验1: 使用 GPT-4")
    print("=" * 60)
    gpt4_api = create_openai_api_call(model="gpt-4")
    game1 = TurtleSoupGame(puzzle, gpt4_api, max_rounds=20, players_config=players)
    log1 = game1.run_game()
    evaluator1 = GameEvaluator(log1, gpt4_api)
    evaluator1.evaluate_all()
    game1.save_game_log("experiment1_gpt4.json")

    # 测试Claude
    print("\n" + "=" * 60)
    print("实验1: 使用 Claude")
    print("=" * 60)
    claude_api = create_anthropic_api_call()
    game2 = TurtleSoupGame(puzzle, claude_api, max_rounds=20, players_config=players)
    log2 = game2.run_game()
    evaluator2 = GameEvaluator(log2, claude_api)
    evaluator2.evaluate_all()
    game2.save_game_log("experiment1_claude.json")


# =============================================================================
# 实验2: 对比不同提问策略的效果
# =============================================================================
def experiment_compare_strategies():
    """对比系统化策略vs创造性策略"""
    with open("test.json", 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    puzzle = puzzles[0]
    api_call = create_openai_api_call(model="gpt-4")

    # 测试两个系统化玩家
    print("=" * 60)
    print("实验2a: 两个系统化玩家")
    print("=" * 60)
    players_systematic = [
        {"name": "系统派A", "strategy": "systematic"},
        {"name": "系统派B", "strategy": "systematic"}
    ]
    game1 = TurtleSoupGame(puzzle, api_call, max_rounds=20, players_config=players_systematic)
    log1 = game1.run_game()
    game1.save_game_log("experiment2_systematic.json")

    # 测试两个创造性玩家
    print("\n" + "=" * 60)
    print("实验2b: 两个创造性玩家")
    print("=" * 60)
    players_creative = [
        {"name": "创意派A", "strategy": "creative"},
        {"name": "创意派B", "strategy": "creative"}
    ]
    game2 = TurtleSoupGame(puzzle, api_call, max_rounds=20, players_config=players_creative)
    log2 = game2.run_game()
    game2.save_game_log("experiment2_creative.json")

    # 测试混合策略
    print("\n" + "=" * 60)
    print("实验2c: 混合策略玩家")
    print("=" * 60)
    players_mixed = [
        {"name": "系统派", "strategy": "systematic"},
        {"name": "创意派", "strategy": "creative"}
    ]
    game3 = TurtleSoupGame(puzzle, api_call, max_rounds=20, players_config=players_mixed)
    log3 = game3.run_game()
    game3.save_game_log("experiment2_mixed.json")


# =============================================================================
# 实验3: 多轮重复实验，测试稳定性
# =============================================================================
def experiment_stability(num_runs=3):
    """对同一谜题进行多次实验，分析稳定性"""
    with open("test.json", 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    puzzle = puzzles[0]
    api_call = create_openai_api_call(model="gpt-4")

    players = [
        {"name": "Player1", "strategy": "systematic"},
        {"name": "Player2", "strategy": "creative"}
    ]

    results = []

    for i in range(num_runs):
        print(f"\n{'=' * 60}")
        print(f"实验3: 第 {i+1}/{num_runs} 轮")
        print('=' * 60)

        game = TurtleSoupGame(puzzle, api_call, max_rounds=20, players_config=players)
        log = game.run_game()

        evaluator = GameEvaluator(log, api_call)
        eval_result = evaluator.evaluate_all()

        game.save_game_log(f"experiment3_run{i+1}.json")
        results.append(eval_result)

    # 分析结果
    print("\n" + "=" * 60)
    print("稳定性分析")
    print("=" * 60)

    coverage_rates = [r["coverage_evaluation"]["coverage_rate"] for r in results]
    print(f"关键问题覆盖率: {coverage_rates}")
    print(f"平均值: {sum(coverage_rates)/len(coverage_rates):.1%}")

    # 保存汇总结果
    with open("experiment3_summary.json", 'w', encoding='utf-8') as f:
        json.dump({
            "num_runs": num_runs,
            "coverage_rates": coverage_rates,
            "all_results": results
        }, f, ensure_ascii=False, indent=2)


# =============================================================================
# 实验4: 不同难度谜题的表现
# =============================================================================
def experiment_difficulty():
    """测试模型在不同难度谜题上的表现"""
    with open("test.json", 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    api_call = create_openai_api_call(model="gpt-4")

    players = [
        {"name": "Player1", "strategy": "systematic"},
        {"name": "Player2", "strategy": "creative"}
    ]

    # 测试前3个谜题（假设难度递增）
    for i, puzzle in enumerate(puzzles[:3]):
        print(f"\n{'=' * 60}")
        print(f"实验4: 谜题 #{i+1}")
        print('=' * 60)
        print(f"汤面: {puzzle['surface']}")

        game = TurtleSoupGame(puzzle, api_call, max_rounds=20, players_config=players)
        log = game.run_game()

        evaluator = GameEvaluator(log, api_call)
        evaluator.evaluate_all()
        evaluator.print_detailed_report()

        game.save_game_log(f"experiment4_puzzle{i+1}.json")


# =============================================================================
# 实验5: 不同玩家数量的影响
# =============================================================================
def experiment_player_count():
    """测试不同数量玩家的效果"""
    with open("test.json", 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    puzzle = puzzles[0]
    api_call = create_openai_api_call(model="gpt-4")

    # 2个玩家
    print("=" * 60)
    print("实验5a: 2个玩家")
    print("=" * 60)
    players_2 = [
        {"name": "Player1", "strategy": "systematic"},
        {"name": "Player2", "strategy": "creative"}
    ]
    game1 = TurtleSoupGame(puzzle, api_call, max_rounds=20, players_config=players_2)
    game1.run_game()
    game1.save_game_log("experiment5_2players.json")

    # 3个玩家
    print("\n" + "=" * 60)
    print("实验5b: 3个玩家")
    print("=" * 60)
    players_3 = [
        {"name": "Player1", "strategy": "systematic"},
        {"name": "Player2", "strategy": "creative"},
        {"name": "Player3", "strategy": "systematic"}
    ]
    game2 = TurtleSoupGame(puzzle, api_call, max_rounds=30, players_config=players_3)
    game2.run_game()
    game2.save_game_log("experiment5_3players.json")

    # 4个玩家
    print("\n" + "=" * 60)
    print("实验5c: 4个玩家")
    print("=" * 60)
    players_4 = [
        {"name": "Player1", "strategy": "systematic"},
        {"name": "Player2", "strategy": "creative"},
        {"name": "Player3", "strategy": "systematic"},
        {"name": "Player4", "strategy": "creative"}
    ]
    game3 = TurtleSoupGame(puzzle, api_call, max_rounds=40, players_config=players_4)
    game3.run_game()
    game3.save_game_log("experiment5_4players.json")


if __name__ == "__main__":
    print("海龟汤游戏 - 实验配置示例")
    print("\n可用的实验:")
    print("1. experiment_compare_models() - 对比不同模型")
    print("2. experiment_compare_strategies() - 对比不同策略")
    print("3. experiment_stability() - 稳定性测试")
    print("4. experiment_difficulty() - 不同难度测试")
    print("5. experiment_player_count() - 不同玩家数量")
    print("\n请在Python中导入并运行相应的函数")
