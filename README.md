# ActivityWatch AI 分类器 (aw-ai-classifier)

这是一个基于 AI 的 ActivityWatch 自动分类工具。它通过分析未分类活动的 App 名称和窗口标题，利用大语言模型（LLM）自动生成分类建议并更新 ActivityWatch 的配置文件。

### 功能特性

*   **自动检测**：通过 [aw_detector.py](aw_detector.py) 获取最近几小时内未匹配现有规则的活动。
*   **AI 智能分类**：利用 [ai_classifier.py](ai_classifier.py) 调用 LLM（如 Llama 3）根据现有分类体系或新类别进行归类。
*   **自动同步配置**：通过 [config_manager.py](config_manager.py) 自动修改 ActivityWatch 的 `settings.json` 文件，添加正则表达式规则。
*   **正则优化**：自动为所有正则规则开启 `ignore_case`（忽略大小写），并对 App 名称进行转义处理。

### 快速开始

#### 1. 安装依赖

确保已安装 Python 3.x，并安装必要的库：

```sh
pip install requests python-dotenv
```

#### 2. 配置环境变量

创建或编辑 [.env](.env) 文件，设置您的 API 密钥和 ActivityWatch 路径：

```env
# LLM 配置
LLM_URL=https://api.groq.com/openai/v1/chat/completions
MODEL_NAME=llama-3.3-70b-versatile
LLM_API_KEY=您的_API_KEY

# ActivityWatch 配置
AW_API_BASE=http://localhost:5600/api/0
# 如果程序找不到 settings.json，请手动指定路径
# AW_SETTINGS_PATH=C:\Users\您的用户名\AppData\Local\activitywatch\activitywatch\aw-server\settings.json
```

#### 3. 运行程序

执行 [main.py](main.py) 开始自动分类：

```sh
python main.py
```

### 项目结构

*   [main.py](main.py): 程序入口，协调检测、分类和配置更新流程。
*   [aw_detector.py](aw_detector.py): 负责从 ActivityWatch API 获取原始事件并进行本地正则匹配过滤。
*   [ai_classifier.py](ai_classifier.py): 封装了与 LLM 交互的逻辑，发送 Prompt 并解析 JSON 响应。
*   [config_manager.py](config_manager.py): 负责读写 ActivityWatch 的 `settings.json` 配置文件。
*   [config.py](config.py): 统一管理环境变量和配置路径。

### 注意事项

*   运行前请确保 ActivityWatch 已经启动。
*   程序会直接修改 ActivityWatch 的配置文件，建议在运行前备份 `settings.json`。
*   默认检测过去 2 小时的活动，您可以在 [main.py](main.py) 中修改 `limit_hours` 参数。

