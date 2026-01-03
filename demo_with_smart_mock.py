"""
智能Mock API演示 - 模拟真实的游戏流程
"""

import json
from game_controller import TurtleSoupGame
from evaluator import GameEvaluator


class SmartMockAPI:
    """智能Mock API，能够根据上下文给出合理的响应"""

    def __init__(self):
        self.call_count = 0
        self.player_questions = {
            "systematic": [
                "[提问] 这个人真的死了吗？",
                "[提问] 他是故意假死的吗？",
                "[提问] 他这样做是为了逃避某些麻烦吗？",
                "[提问] 他去了一个偏远的地方吗？",
                "[最终推理] 我认为这个人为了逃避某些危险（可能是犯罪组织或法律问题），故意假装自己死了，然后躲到了一个偏远的岛屿，后来给家人寄信报平安。"
            ],
            "creative": [
                "[提问] 信是在他被宣布死亡之后寄出的吗？",
                "[提问] 他和家人之间有什么秘密吗？",
                "[提问] 他涉及非法活动吗？",
                "[提问] 他有特殊的生存技能吗？",
                "[最终推理] 这个人可能因为卷入非法活动而被追杀，他利用自己的生存技能精心策划了假死，逃到了一个偏远岛屿。他在那里安顿下来后，给家人写信告诉他们真相，但要求保密。"
            ]
        }
        self.current_player_index = {"systematic": 0, "creative": 0}

    def __call__(self, system_prompt: str, user_prompt: str) -> str:
        """模拟API调用"""
        self.call_count += 1

        # 主持人回答
        if "主持人" in system_prompt and "基于你掌握的故事真相" in user_prompt:
            # 提取玩家的问题
            if "真的死了吗" in user_prompt or "really dead" in user_prompt.lower():
                return "否。他没有真的死。"
            elif "假死" in user_prompt or "fake" in user_prompt.lower():
                return "是。他是故意假死的。"
            elif "非法" in user_prompt or "犯罪" in user_prompt or "illegal" in user_prompt.lower():
                return "是。他涉及了非法活动。"
            elif "偏远" in user_prompt or "岛" in user_prompt or "island" in user_prompt.lower():
                return "是。他去了一个偏远的岛屿。"
            elif "生存技能" in user_prompt or "survival" in user_prompt.lower():
                return "是。他有生存技能。"
            elif "逃避" in user_prompt or "escape" in user_prompt.lower():
                return "是。他在逃避追捕。"
            elif "家人" in user_prompt or "family" in user_prompt.lower():
                return "是。他后来联系了家人。"
            elif "秘密" in user_prompt or "secret" in user_prompt.lower():
                return "是。这需要保密。"
            else:
                return "不重要。这个细节对解谜不太重要。"

        # 玩家提问
        elif "玩家" in system_prompt:
            # 判断是哪个玩家
            if "系统派" in system_prompt or "systematic" in system_prompt.lower():
                strategy = "systematic"
            elif "创意派" in system_prompt or "creative" in system_prompt.lower():
                strategy = "creative"
            elif "探索者" in system_prompt:
                strategy = "systematic"
            elif "直觉派" in system_prompt:
                strategy = "creative"
            else:
                strategy = "systematic"

            # 检查是否要求最终推理
            if "最终推理" in user_prompt:
                return self.player_questions[strategy][-1]

            # 返回下一个问题
            idx = self.current_player_index[strategy]
            if idx < len(self.player_questions[strategy]) - 1:  # 减1因为最后一个是最终推理
                question = self.player_questions[strategy][idx]
                self.current_player_index[strategy] += 1
                return question
            else:
                # 问题用完了，给出推理
                return self.player_questions[strategy][-1]

        # 评估响应
        elif "评估专家" in system_prompt:
            if "覆盖" in user_prompt or "coverage" in user_prompt.lower():
                # 判断关键问题覆盖
                if "fake" in user_prompt.lower() or "假死" in user_prompt:
                    return "是\n玩家的问题中提到了'他是故意假死的吗'，这覆盖了该关键问题。"
                elif "illegal" in user_prompt.lower() or "非法" in user_prompt:
                    return "是\n玩家问到了'他涉及非法活动吗'，覆盖了这个关键点。"
                elif "island" in user_prompt.lower() or "岛" in user_prompt:
                    return "是\n玩家询问了'他去了一个偏远的地方吗'，涉及了岛屿这个关键信息。"
                elif "survival" in user_prompt.lower() or "生存" in user_prompt:
                    return "是\n玩家提到了'他有特殊的生存技能吗'，覆盖了这一点。"
                else:
                    return "否\n玩家的问题中没有明确涉及这个关键点。"
            else:
                # 评分响应
                return """核心情节：8/10 - 玩家准确识别了假死逃亡的核心情节
关键细节：7/10 - 提到了非法活动、偏远岛屿等关键细节
逻辑推理：8/10 - 推理过程符合逻辑，从假死推导到逃避追捕
整体完整度：7/10 - 基本完整，但缺少一些具体细节如帮助者等
总体评分：75/100"""

        return "Mock响应"


def main():
    print("="*60)
    print("智能Mock API演示 - 海龟汤游戏")
    print("="*60)

    # 加载谜题
    with open("test.json", 'r', encoding='utf-8') as f:
        puzzles = json.load(f)

    puzzle = puzzles[0]

    # 创建智能Mock API
    api = SmartMockAPI()

    # 配置玩家
    players = [
        {"name": "系统派", "strategy": "systematic"},
        {"name": "创意派", "strategy": "creative"}
    ]

    # 运行游戏
    game = TurtleSoupGame(puzzle, api, max_rounds=12, players_config=players)
    log = game.run_game()

    # 评估
    print("\n" + "="*60)
    print("开始评估...")
    print("="*60)

    evaluator = GameEvaluator(log, api)
    evaluator.evaluate_all()
    evaluator.print_detailed_report()

    # 保存日志
    game.save_game_log("demo_game_log.json")

    print("\n" + "="*60)
    print("演示完成！")
    print("="*60)
    print(f"\n游戏日志已保存到: demo_game_log.json")
    print(f"总共进行了 {log['total_rounds']} 个回合")
    print(f"API调用次数: {api.call_count}")


if __name__ == "__main__":
    main()
