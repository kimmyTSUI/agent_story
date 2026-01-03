"""
游戏评估器
评估玩家的表现，包括问题质量和最终答案的准确性
"""

from typing import Dict, List, Callable
import re


class GameEvaluator:
    """
    评估玩家在海龟汤游戏中的表现
    """

    def __init__(self, game_log: Dict, model_api_call: Callable):
        """
        初始化评估器

        Args:
            game_log: 游戏日志
            model_api_call: 调用LLM的函数
        """
        self.game_log = game_log
        self.model_api_call = model_api_call
        self.key_questions = game_log["key_questions"]
        self.bottom = game_log["bottom"]

    def evaluate_question_coverage(self) -> Dict:
        """
        评估玩家提出的问题是否覆盖了关键问题

        Returns:
            评估结果，包括覆盖的关键问题和覆盖率
        """
        # 提取所有玩家提出的问题
        player_questions = [
            round_info["question"]
            for round_info in self.game_log["rounds"]
            if not round_info.get("is_guess", False)
        ]

        # 使用LLM判断每个关键问题是否被覆盖
        coverage_results = {}

        for key_q in self.key_questions:
            system_prompt = """你是一个评估专家，需要判断玩家的提问是否覆盖了关键问题。

关键问题不需要字面上完全一致，只要语义上询问了相同或相关的内容即可。"""

            user_prompt = f"""**关键问题：**
{key_q}

**玩家提出的所有问题：**
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(player_questions)])}

请判断玩家的问题中是否有覆盖到这个关键问题（语义相似即可）。

回答格式：
是/否
[如果是，请说明是哪个问题]
"""

            response = self.model_api_call(system_prompt, user_prompt)
            is_covered = response.strip().startswith("是")

            coverage_results[key_q] = {
                "covered": is_covered,
                "response": response
            }

        # 计算覆盖率
        covered_count = sum(1 for result in coverage_results.values() if result["covered"])
        coverage_rate = covered_count / len(self.key_questions) if self.key_questions else 0

        return {
            "coverage_details": coverage_results,
            "covered_count": covered_count,
            "total_key_questions": len(self.key_questions),
            "coverage_rate": coverage_rate
        }

    def evaluate_final_guess(self, player_name: str) -> Dict:
        """
        评估玩家最终推理的准确性

        Args:
            player_name: 玩家名称

        Returns:
            评估结果
        """
        final_guess = self.game_log["final_guesses"].get(player_name, "")

        system_prompt = """你是一个评估专家，需要评估玩家的推理与真相的相似度。

请从以下维度评估：
1. 核心情节是否正确（0-10分）
2. 关键细节是否准确（0-10分）
3. 逻辑推理是否合理（0-10分）
4. 整体完整度（0-10分）

并给出总体评分（0-100分）。"""

        user_prompt = f"""**真相：**
{self.bottom}

**玩家推理：**
{final_guess}

请按照以下格式评估：
核心情节：X/10 - 简要说明
关键细节：X/10 - 简要说明
逻辑推理：X/10 - 简要说明
整体完整度：X/10 - 简要说明
总体评分：X/100
"""

        response = self.model_api_call(system_prompt, user_prompt)

        # 解析评分
        scores = self._parse_scores(response)

        return {
            "player_name": player_name,
            "final_guess": final_guess,
            "evaluation_response": response,
            "scores": scores
        }

    def _parse_scores(self, response: str) -> Dict:
        """
        从评估响应中解析分数

        Args:
            response: LLM的评估响应

        Returns:
            分数字典
        """
        scores = {
            "core_plot": 0,
            "key_details": 0,
            "logical_reasoning": 0,
            "completeness": 0,
            "total": 0
        }

        # 使用正则表达式提取分数
        patterns = {
            "core_plot": r"核心情节[：:]\s*(\d+)/10",
            "key_details": r"关键细节[：:]\s*(\d+)/10",
            "logical_reasoning": r"逻辑推理[：:]\s*(\d+)/10",
            "completeness": r"整体完整度[：:]\s*(\d+)/10",
            "total": r"总体评分[：:]\s*(\d+)/100"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, response)
            if match:
                scores[key] = int(match.group(1))

        return scores

    def evaluate_game_efficiency(self) -> Dict:
        """
        评估游戏效率（用了多少回合，问题质量等）

        Returns:
            效率评估结果
        """
        total_rounds = self.game_log["total_rounds"]
        max_rounds = self.game_log["max_rounds"]

        # 统计每个玩家的提问次数
        player_stats = {}
        for round_info in self.game_log["rounds"]:
            player = round_info["player"]
            if player not in player_stats:
                player_stats[player] = {
                    "questions": 0,
                    "guesses": 0
                }

            if round_info.get("is_guess", False):
                player_stats[player]["guesses"] += 1
            else:
                player_stats[player]["questions"] += 1

        return {
            "total_rounds": total_rounds,
            "max_rounds": max_rounds,
            "efficiency_rate": 1 - (total_rounds / max_rounds) if max_rounds > 0 else 0,
            "player_stats": player_stats
        }

    def evaluate_all(self) -> Dict:
        """
        执行完整评估

        Returns:
            完整评估结果
        """
        print("\n" + "="*60)
        print("开始评估游戏表现...")
        print("="*60)

        # 评估问题覆盖率
        print("\n1. 评估关键问题覆盖率...")
        coverage_eval = self.evaluate_question_coverage()
        print(f"   覆盖了 {coverage_eval['covered_count']}/{coverage_eval['total_key_questions']} 个关键问题")
        print(f"   覆盖率: {coverage_eval['coverage_rate']:.1%}")

        # 评估每个玩家的最终推理
        print("\n2. 评估玩家最终推理...")
        player_evaluations = {}
        for player_name in self.game_log["final_guesses"].keys():
            print(f"   评估 {player_name}...")
            player_eval = self.evaluate_final_guess(player_name)
            player_evaluations[player_name] = player_eval
            print(f"   {player_name} 总分: {player_eval['scores']['total']}/100")

        # 评估游戏效率
        print("\n3. 评估游戏效率...")
        efficiency_eval = self.evaluate_game_efficiency()
        print(f"   使用回合数: {efficiency_eval['total_rounds']}/{efficiency_eval['max_rounds']}")

        evaluation_result = {
            "coverage_evaluation": coverage_eval,
            "player_evaluations": player_evaluations,
            "efficiency_evaluation": efficiency_eval
        }

        # 将评估结果添加到游戏日志
        self.game_log["evaluation"] = evaluation_result

        print("\n" + "="*60)
        print("评估完成！")
        print("="*60)

        return evaluation_result

    def print_detailed_report(self):
        """
        打印详细评估报告
        """
        if "evaluation" not in self.game_log:
            print("请先运行 evaluate_all() 方法")
            return

        eval_result = self.game_log["evaluation"]

        print("\n" + "#"*60)
        print("详细评估报告")
        print("#"*60)

        # 关键问题覆盖率
        print("\n【关键问题覆盖情况】")
        coverage = eval_result["coverage_evaluation"]
        print(f"覆盖率: {coverage['coverage_rate']:.1%} ({coverage['covered_count']}/{coverage['total_key_questions']})")
        print("\n详细情况:")
        for i, (key_q, result) in enumerate(coverage["coverage_details"].items(), 1):
            status = "✓" if result["covered"] else "✗"
            print(f"{i}. {status} {key_q}")

        # 玩家评分
        print("\n【玩家表现评分】")
        for player_name, player_eval in eval_result["player_evaluations"].items():
            scores = player_eval["scores"]
            print(f"\n{player_name}:")
            print(f"  核心情节: {scores['core_plot']}/10")
            print(f"  关键细节: {scores['key_details']}/10")
            print(f"  逻辑推理: {scores['logical_reasoning']}/10")
            print(f"  整体完整度: {scores['completeness']}/10")
            print(f"  总体评分: {scores['total']}/100")

        # 游戏效率
        print("\n【游戏效率】")
        efficiency = eval_result["efficiency_evaluation"]
        print(f"回合使用: {efficiency['total_rounds']}/{efficiency['max_rounds']}")
        print(f"效率评分: {efficiency['efficiency_rate']:.1%}")
        print("\n各玩家提问统计:")
        for player, stats in efficiency["player_stats"].items():
            print(f"  {player}: {stats['questions']} 个问题, {stats['guesses']} 次推理")

        print("\n" + "#"*60)
