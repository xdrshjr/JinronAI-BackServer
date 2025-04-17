# 多MCP客户端

这是一个能够同时连接多个MCP(Model Context Protocol)服务器的客户端程序，让语言模型能够自主选择使用哪个MCP服务来完成任务。

## 功能特点

- 自动从配置文件读取所有MCP服务器配置
- 自动启动并连接到所有MCP后台服务
- 将所有可用工具集成到一个统一的会话中
- 让LLM自行决定使用哪个MCP后台服务来处理用户请求
- 自动停止所有服务器进程
- 支持命令行参数自定义配置文件和API设置

## 安装依赖

```bash
pip install anthropic mcp python-dotenv
```

## 使用方法

### 基本用法

1. 确保您已经在配置文件中配置了MCP服务器信息
2. 运行多MCP客户端程序：

```bash
python multi_mcp_client.py
```

3. 输入您的问题，让语言模型选择合适的MCP服务来处理
4. 输入`quit`退出程序

### 命令行参数

程序支持以下命令行参数：

- `--config` 或 `-c`: 指定配置文件路径（默认：`config/mcp-server-config-example.json`）
- `--api-url`: 指定LLM API的URL（默认：`https://xiaoai.plus/`）
- `--api-key`: 指定LLM API的密钥

例如，使用本地Python MCP服务器配置：

```bash
python multi_mcp_client.py --config config/local-mcp-server-config.json
```

## 配置文件

### 标准配置文件

标准配置文件位于`config/mcp-server-config-example.json`，格式如下：

```json
{
  "systemPrompt": "系统提示信息...",
  "llm": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key": "your-api-key-here",
    "temperature": 0
  },
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-brave-api-key-here"
      }
    },
    "youtube": {
      "command": "npx",
      "args": ["-y", "github:anaisbetts/mcp-youtube"]
    },
    "mcp-server-commands": {
      "command": "npx",
      "args": ["mcp-server-commands"],
      "requires_confirmation": [
        "run_command",
        "run_script"
      ]
    }
  }
}
```

### 本地Python MCP服务器配置

如果您遇到`npx`或`uvx`命令不可用的问题，可以使用内置的Python MCP服务器。配置文件位于`config/local-mcp-server-config.json`：

```json
{
  "systemPrompt": "您是一个AI助手，帮助用户完成各种任务。今天是 {today_datetime}。我旨在提供清晰、准确和有用的回应。",
  "llm": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "api_key": "your-api-key-here",
    "temperature": 0
  },
  "mcpServers": {
    "python-commands": {
      "command": "python",
      "args": ["-m", "mcp.server.commands"],
      "requires_confirmation": [
        "run_command",
        "run_script"
      ]
    },
    "python-fileio": {
      "command": "python",
      "args": ["-m", "mcp.server.fileio"]
    }
  }
}
```

您可以根据需要添加或修改MCP服务器配置。

## 服务器配置项说明

每个MCP服务器配置需要包含以下信息：

- `command`：启动服务器的命令（如`npx`、`python`等）
- `args`：命令行参数列表
- `env`（可选）：环境变量
- `requires_confirmation`（可选）：需要用户确认的工具名称列表

## 故障排除

如果您在运行程序时遇到以下错误：
```
启动服务器 xxx 失败: [WinError 2] 系统找不到指定的文件。
```

可能的解决方案：
1. 确保已安装Node.js（对于`npx`命令）
2. 确保已安装相关工具（如`uvx`）
3. 使用Python内置的MCP服务器：`python multi_mcp_client.py --config config/local-mcp-server-config.json`

## 注意事项

- 确保您已经安装了所有MCP服务器依赖
- 部分MCP服务可能需要特定的API密钥，请在配置文件中提供
- 当程序退出时，所有MCP服务器进程将被自动终止 