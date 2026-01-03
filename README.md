# 海龟汤游戏 - Agent推理实验框架

这是一个用于研究LLM Agent推理能力的实验框架，通过让多个Agent玩海龟汤（情景推理）游戏来评估它们的推理、提问和协作能力。

## 游戏规则

**海龟汤**是一种情景推理游戏：
- **主持人**：给出一个看似矛盾或不可思议的"汤面"（谜题），知道完整的"汤底"（真相）
- **玩家**：通过提出只能用"是"、"否"或"不重要"回答的问题，逐步推理出真相

## 框架架构

### 核心组件

1. **agents.py** - Agent定义
   - `HostAgent`: 主持人Agent，负责给出谜题并回答是非问题
   - `PlayerAgent`: 玩家Agent，负责提问和推理

2. **game_controller.py** - 游戏控制器
   - `TurtleSoupGame`: 管理游戏流程，协调主持人和玩家的交互

3. **evaluator.py** - 评估器
   - `GameEvaluator`: 评估玩家表现，包括问题覆盖率、答案准确性等

4. **run_experiment.py** - 实验运行脚本
   - 支持OpenAI API、Anthropic API
   - 包含Mock API用于测试

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备API密钥

根据你选择的LLM服务，设置环境变量：

```bash
# 使用OpenAI
export OPENAI_API_KEY="your-api-key"

# 或使用Anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

### 3. 运行实验

#### 方式1: 使用主运行脚本（交互式）

```bash
python run_experiment.py
```

然后根据提示选择API类型（OpenAI/Anthropic/Mock）。

#### 方式2: 使用简单示例

```bash
python example_simple.py
```

这会使用Mock API运行一个演示游戏。

### 4. 使用真实API的代码示例

```python
import json
from game_controller import TurtleSoupGame
from evaluator import GameEvaluator
from run_experiment import create_openai_api_call

# 加载谜题
with open("test.json", 'r', encoding='utf-8') as f:
    puzzles = json.load(f)

puzzle = puzzles[0]

# 创建API调用函数
api_call = create_openai_api_call(model="gpt-4")

# 配置玩家
players = [
    {"name": "系统派", "strategy": "systematic"},
    {"name": "创意派", "strategy": "creative"}
]

# 运行游戏
game = TurtleSoupGame(puzzle, api_call, max_rounds=20, players_config=players)
game_log = game.run_game()

# 评估
evaluator = GameEvaluator(game_log, api_call)
evaluator.evaluate_all()
evaluator.print_detailed_report()

# 保存日志
game.save_game_log("my_game_log.json")
```

## 数据集格式

`test.json` 包含多个谜题，每个谜题的格式如下：

```json
{
  "index": 1,
  "surface": "谜题描述（汤面）",
  "bottom": "完整故事真相（汤底）",
  "key_question": ["关键问题1", "关键问题2", ...],
  "story_tree": { "故事推理树结构" },
  "supernatural": false,
  "someone_dies": true
}
```

## 评估指标

框架会自动评估以下方面：

1. **关键问题覆盖率**
   - 玩家提出的问题是否覆盖了数据集中的关键问题
   - 计算覆盖率百分比

2. **最终答案质量**
   - 核心情节准确性 (0-10分)
   - 关键细节准确性 (0-10分)
   - 逻辑推理合理性 (0-10分)
   - 整体完整度 (0-10分)
   - 总体评分 (0-100分)

3. **游戏效率**
   - 使用的回合数
   - 每个玩家的提问统计

## 玩家策略

框架支持不同的提问策略：

- **systematic（系统化）**: 按逻辑顺序，从基本事实到细节
- **creative（创造性）**: 大胆假设，从不同角度思考

你可以在配置中自定义策略。

## 输出文件

游戏结束后会生成JSON日志文件，包含：
- 完整对话历史
- 每个回合的问答记录
- 玩家的最终推理
- 详细的评估结果

## 自定义使用

### 添加新的LLM API

```python
def create_custom_api_call():
    def api_call(system_prompt: str, user_prompt: str) -> str:
        # 你的API调用逻辑
        response = your_llm_client.chat(system_prompt, user_prompt)
        return response
    return api_call
```

### 修改评估标准

你可以继承 `GameEvaluator` 类并重写评估方法来自定义评估逻辑。

### 添加更多玩家

```python
players_config = [
    {"name": "Player1", "strategy": "systematic"},
    {"name": "Player2", "strategy": "creative"},
    {"name": "Player3", "strategy": "systematic"},
    # 可以添加任意数量的玩家
]
```

## 实验建议

1. **对比不同模型**: 使用相同谜题测试不同的LLM模型
2. **对比不同策略**: 让相同模型使用不同的提问策略
3. **多轮实验**: 对同一谜题进行多次实验，分析稳定性
4. **难度分析**: 使用不同难度的谜题评估模型能力

## 文件结构

```
agent_story/
├── agents.py              # Agent定义
├── game_controller.py     # 游戏控制器
├── evaluator.py           # 评估器
├── run_experiment.py      # 主运行脚本
├── example_simple.py      # 简单示例
├── test.json              # 谜题数据集
├── requirements.txt       # 依赖包
└── README.md             # 本文档
```

## 许可证

本项目用于学术研究和教育目的。
