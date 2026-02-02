"""
海龟汤游戏的Agent定义
包括主持人Agent和玩家Agent
"""

from typing import Dict, List, Optional
import json


class HostAgent:
    """
    主持人Agent - 负责给出汤面并回答玩家的是非问题
    """

    def __init__(self, puzzle_data: Dict):
        """
        初始化主持人Agent

        Args:
            puzzle_data: 包含surface、bottom、key_question等信息的谜题数据
        """
        self.surface = puzzle_data["surface"]
        self.bottom = puzzle_data["bottom"]
        self.key_questions = puzzle_data["key_question"]
        self.story_tree = puzzle_data["story_tree"]

    def get_system_prompt(self) -> str:
        """生成主持人的系统提示"""
        return f"""你是一个海龟汤游戏的主持人。你知道完整的故事真相。

**汤面（谜题）：**
{self.surface}

**汤底（真相）：**
{self.bottom}

**你的职责：**
1. 对玩家的提问，只能回答"是"、"否"或"不相关"
2. 如果问题与真相相符，回答"是"
3. 如果问题与真相不符，回答"否"
4. 如果问题对解开谜题不相关，回答"不相关"
5. 不要透露任何超出是非回答的信息
6. 保持神秘感，让玩家自己推理

**回答格式：**
只需回答：是/否/不相关

**示例：**
玩家："这个人真的死了吗？"
主持人："否。"

玩家："天气与此有关吗？"
主持人："不相关。"
"""

    def answer_question(self, question: str, model_api_call) -> str:
        """
        根据问题回答是/否/不相关

        Args:
            question: 玩家的问题
            model_api_call: 调用LLM的函数

        Returns:
            主持人的回答
        """
        prompt = f"""基于你掌握的故事真相，请回答玩家的问题。

玩家问题：{question}

请只回答"是"、"否"或"不相关"。"""

        response = model_api_call(self.get_system_prompt(), prompt)
        return self.normalize_answer(response)

    def evaluate_guess(self, guess: str, model_api_call) -> str:
        """
        判断玩家的推理是否与真相一致

        Args:
            guess: 玩家推理内容
            model_api_call: 调用LLM的函数

        Returns:
            主持人的回答（是/否）
        """
        prompt = f"""基于你掌握的故事真相，请判断玩家的推理是否与真相一致。

玩家推理：{guess}

请只回答"是"或"否"。"""

        response = model_api_call(self.get_system_prompt(), prompt)
        normalized = self.normalize_answer(response)
        return "是" if normalized == "是" else "否"

    @staticmethod
    def normalize_answer(response: str) -> str:
        """
        将模型回答规范化为 是/否/不相关
        """
        if not response:
            return "不相关"

        cleaned = response.strip()
        if "不相关" in cleaned or "无关" in cleaned or "不重要" in cleaned:
            return "不相关"
        if "是" in cleaned or "yes" in cleaned.lower():
            return "是"
        if "否" in cleaned or "no" in cleaned.lower():
            return "否"
        return "不相关"


class PlayerAgent:
    """
    玩家Agent - 通过提问来推理汤底
    """

    def __init__(self, player_name: str, strategy: str = "systematic"):
        """
        初始化玩家Agent

        Args:
            player_name: 玩家名称（如"Player1"、"Player2"）
            strategy: 提问策略（systematic=系统化提问, creative=创造性提问）
        """
        self.player_name = player_name
        self.strategy = strategy
        self.conversation_history = []

    def get_system_prompt(self, surface: str) -> str:
        """生成玩家的系统提示"""
        strategy_guide = {
            "systematic": """你应该采用系统化的提问策略：
1. 先确认基本事实（人物、地点、时间）
2. 排除明显的可能性
3. 逐步缩小范围
4. 关注异常点和矛盾之处""",
            "creative": """你应该采用创造性的提问策略：
1. 大胆假设，从不同角度思考
2. 关注细节和隐藏信息
3. 尝试反常识的可能性
4. 寻找故事中的关键转折点"""
        }

        return f"""你是海龟汤游戏的玩家{self.player_name}。你需要通过提出是非问题来解开谜题。

**汤面（已知信息）：**
{surface}

**游戏规则：**
1. 你只能提出可以用"是"、"否"或"不相关"回答的问题
2. 根据主持人的回答逐步推理出完整故事
3. 当你认为已经了解真相时，可以说出你的推理

**你的策略：**
{strategy_guide.get(self.strategy, strategy_guide["systematic"])}

**注意：**
- 每次只提一个问题
- 基于之前的对话历史进行推理
- 问题要具体且有针对性
- 避免重复已经确认的信息

**回答格式：**
[提问] 你的问题
或
[推理] 你认为的完整故事
"""

    def ask_question(self, surface: str, conversation_history: List[Dict], model_api_call) -> str:
        """
        基于当前信息提出问题

        Args:
            surface: 汤面
            conversation_history: 对话历史
            model_api_call: 调用LLM的函数

        Returns:
            玩家的问题或推理
        """
        # 构建对话历史
        history_text = "\n".join([
            f"{item['player']}: {item['question']}\n主持人: {item['answer']}"
            for item in conversation_history
        ])

        prompt = f"""**对话历史：**
{history_text if history_text else "（还没有提问记录）"}

现在轮到你{self.player_name}了。请根据汤面和对话历史，提出你的下一个问题或给出你的推理。

格式：
[提问] 你的问题
或
[推理] 你的完整推理
"""

        return model_api_call(self.get_system_prompt(surface), prompt)

    def make_final_guess(self, surface: str, conversation_history: List[Dict], model_api_call) -> str:
        """
        做出最终推理

        Args:
            surface: 汤面
            conversation_history: 对话历史
            model_api_call: 调用LLM的函数

        Returns:
            玩家的最终推理
        """
        history_text = "\n".join([
            f"{item['player']}: {item['question']}\n主持人: {item['answer']}"
            for item in conversation_history
        ])

        prompt = f"""**对话历史：**
{history_text}

现在请你给出最终推理，说出你认为的完整故事真相。请尽可能详细和完整。

[最终推理]
"""

        return model_api_call(self.get_system_prompt(surface), prompt)
