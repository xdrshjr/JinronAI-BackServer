import asyncio
import json
import os
import subprocess
import sys
import shutil
import argparse
import time
from typing import Dict, List, Optional, Any
from contextlib import AsyncExitStack
import aiohttp  # 添加这个导入

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # 加载.env文件中的环境变量

# 添加命令行参数解析
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='多MCP服务器客户端')
    parser.add_argument('--config', '-c', 
                        default="config/mcp-server-config-example.json",
                        help='配置文件路径 (默认: config/mcp-server-config-example.json)')
    parser.add_argument('--api-url', 
                        default="https://xiaoai.plus",
                        help='LLM API的URL (默认: https://xiaoai.plus/v1)')
    parser.add_argument('--api-key', 
                        default="sk-PagpyNwAitZjhGzzrWKUssACvvFk28U8O4dmypPxEkrRo2jh",
                        help='LLM API的密钥')
    parser.add_argument('--connect-timeout',
                        type=int,
                        default=30,
                        help='连接服务器的超时时间（秒）(默认: 30)')
    parser.add_argument('--debug',
                        action='store_true',
                        help='启用调试模式，输出更详细的日志')
    
    return parser.parse_args()

class MCPServerManager:
    """管理多个MCP服务器的类"""
    
    def __init__(self, config_path: str = "config/mcp-server-config-example.json", debug: bool = False):
        """
        初始化MCP服务器管理器
        
        Args:
            config_path: MCP服务器配置文件路径
            debug: 是否启用调试模式
        """
        self.config_path = config_path
        self.debug = debug
        self.config = self._load_config()
        self.server_processes = {}
        
    def _load_config(self) -> dict:
        """加载配置文件"""
        try:
            if self.debug:
                print(f"正在加载配置文件: {self.config_path}")
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if self.debug:
                    print(f"配置文件加载成功，找到 {len(config.get('mcpServers', {}))} 个服务器配置")
                return config
        except Exception as e:
            print(f"无法加载配置文件: {str(e)}")
            sys.exit(1)
    
    def _command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        return shutil.which(command) is not None
    
    def start_servers(self) -> Dict[str, subprocess.Popen]:
        """启动所有配置的MCP服务器"""
        servers_config = self.config.get("mcpServers", {})
        success_count = 0
        failure_count = 0
        
        if self.debug:
            print(f"准备启动 {len(servers_config)} 个MCP服务器")
        
        for server_name, server_config in servers_config.items():
            try:
                command = server_config.get("command")
                args = server_config.get("args", [])
                env_vars = server_config.get("env", {})
                
                # 检查命令是否存在
                if not self._command_exists(command):
                    print(f"警告: 命令 '{command}' 不存在或不在PATH中。请确保已安装相关工具。")
                    print(f"如果使用 npm/npx，请确保已安装 Node.js 并添加到PATH中。")
                    print(f"如果使用 uvx 等特定工具，请确保已正确安装。")
                    failure_count += 1
                    continue
                
                # 合并环境变量
                env = os.environ.copy()
                env.update(env_vars)
                
                # 构建完整命令
                full_command = [command] + args
                
                print(f"启动服务器 {server_name}: {' '.join(full_command)}")
                
                # 启动进程
                process = subprocess.Popen(
                    full_command,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 检查进程是否立即退出
                time.sleep(0.2)  # 等待一小段时间
                if process.poll() is not None:
                    if self.debug:
                        stdout, stderr = process.communicate()
                        print(f"服务器 {server_name} 启动失败，进程已退出，退出码: {process.returncode}")
                        print(f"标准输出: {stdout}")
                        print(f"标准错误: {stderr}")
                    else:
                        print(f"服务器 {server_name} 启动失败，进程已退出，退出码: {process.returncode}")
                    failure_count += 1
                    continue
                
                self.server_processes[server_name] = process
                print(f"服务器 {server_name} 已启动，PID: {process.pid}")
                success_count += 1
                
            except Exception as e:
                print(f"启动服务器 {server_name} 失败: {str(e)}")
                failure_count += 1
        
        # 打印摘要信息
        print(f"\n服务器启动摘要:")
        print(f"成功: {success_count}, 失败: {failure_count}")
        
        if not self.server_processes:
            print("\n警告: 没有任何MCP服务器成功启动!")
            print("建议操作:")
            print("1. 确保已安装 Node.js 并将其添加到系统PATH中")
            print("2. 尝试手动运行配置中的命令以检查错误详情")
            print("3. 调整配置文件中的命令路径")
            print("4. 使用 --config 参数指定不同的配置文件")
            print("\n尽管如此，程序将继续运行，但所有LLM请求将不使用任何工具。")
        
        return self.server_processes
    
    def stop_servers(self):
        """停止所有MCP服务器"""
        if not self.server_processes:
            print("没有需要停止的服务器。")
            return
            
        for server_name, process in self.server_processes.items():
            try:
                print(f"停止服务器 {server_name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"服务器 {server_name} 已停止")
            except Exception as e:
                print(f"停止服务器 {server_name} 失败: {str(e)}")
                try:
                    process.kill()
                except:
                    pass

class MultiMCPClient:
    """多MCP服务器客户端"""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, 
                 config_path: str = "config/mcp-server-config-example.json",
                 connect_timeout: int = 30, debug: bool = False):
        """
        初始化多MCP客户端
        
        Args:
            api_url: LLM API的URL
            api_key: LLM API的密钥
            config_path: 配置文件路径
            connect_timeout: 连接超时时间（秒）
            debug: 是否启用调试模式
        """
        # 初始化会话和客户端对象
        self.sessions = {}
        self.exit_stack = AsyncExitStack()
        self.connect_timeout = connect_timeout
        self.debug = debug
        
        # 使用提供的API参数
        self.api_key = api_key
        self.api_url = api_url
        
        if self.debug:
            print(f"初始化Anthropic客户端，API URL: {api_url}")
        
        # 初始化Anthropic客户端
        anthropic_kwargs = {}
        if self.api_key:
            anthropic_kwargs["api_key"] = self.api_key
        if self.api_url:
            anthropic_kwargs["base_url"] = self.api_url
            
        self.anthropic = Anthropic(**anthropic_kwargs)
        
        # 加载配置
        self.config_path = config_path
        if self.debug:
            print(f"加载配置文件: {config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    async def _connect_server(self, server_params: StdioServerParameters) -> tuple:
        """建立服务器连接并初始化会话的辅助方法"""
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        
        await session.initialize()
        
        # 获取可用工具列表
        response = await session.list_tools()
        return session, response.tools, stdio, write
    
    async def connect_to_server_with_timeout(self, server_name: str, server_config: dict) -> bool:
        """
        使用超时连接到单个服务器
        
        Args:
            server_name: 服务器名称
            server_config: 服务器配置

        Returns:
            是否连接成功
        """
        try:
            if self.debug:
                print(f"尝试连接到服务器 {server_name}...")
                
            command = server_config.get("command")
            args = server_config.get("args", [])
            
            # 创建参数字符串用于显示
            args_str = " ".join(args)
            server_info = f"{command} {args_str}"
            
            # 对于不同类型的服务器，可能需要不同的连接方式
            # 这里假设所有服务器都是通过stdio连接
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=server_config.get("env")
            )
            
            # 使用wait_for函数来设置超时（兼容Python 3.10及以下版本）
            try:
                # 尝试建立连接
                session, tools, stdio, write = await asyncio.wait_for(
                    self._connect_server(server_params),
                    timeout=self.connect_timeout
                )
                
                print(f"\n已连接到服务器 {server_name} 工具: {[tool.name for tool in tools]}")
                
                # 保存会话供后续使用
                self.sessions[server_name] = {
                    "session": session,
                    "tools": tools,
                    "stdio": stdio,
                    "write": write
                }
                return True
                    
            except asyncio.TimeoutError:
                print(f"连接到服务器 {server_name} 超时（{self.connect_timeout}秒）")
                return False
                
        except Exception as e:
            print(f"连接到服务器 {server_name} 失败: {str(e)}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return False
    
    async def connect_to_servers(self, server_data: Dict[str, subprocess.Popen]):
        """
        连接到所有启动的MCP服务器
        
        Args:
            server_data: 服务器名称和进程的字典
        """
        print("\n正在连接到MCP服务器...")
        
        if not server_data:
            print("没有已启动的MCP服务器可连接。")
            return
        
        server_count = len(server_data)
        success_count = 0
        
        # 并行连接所有服务器，但有超时限制
        connect_tasks = []
        for server_name in server_data.keys():
            if self.debug:
                print(f"准备连接到服务器: {server_name}")
            server_config = self.config["mcpServers"][server_name]
            connect_tasks.append(self.connect_to_server_with_timeout(server_name, server_config))
        
        # 等待所有连接任务完成
        results = await asyncio.gather(*connect_tasks)
        success_count = sum(1 for result in results if result)
        
        # 打印摘要信息
        print(f"\n服务器连接摘要:")
        print(f"成功: {success_count}, 失败: {server_count - success_count}")
        
        if self.debug:
            print(f"已连接的服务器: {list(self.sessions.keys())}")

    async def process_query(self, query: str) -> str:
        # 修改此方法，添加更多的错误处理和调试信息
        if self.debug:
            print(f"处理查询: {query}")
            print(f"可用会话: {list(self.sessions.keys())}")

        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # 收集所有可用工具
        all_tools = []
        for server_name, server_data in self.sessions.items():
            for tool in server_data["tools"]:
                # 添加服务器名称前缀，以便后续识别
                tool_with_prefix = {
                    "name": f"{server_name}.{tool.name}",
                    "description": f"[{server_name}] {tool.description}",
                    "input_schema": tool.inputSchema
                }
                all_tools.append(tool_with_prefix)

        if self.debug:
            print(f"收集到 {len(all_tools)} 个可用工具")

        final_text = []

        # 初始对话
        try:
            # 增加超时设置和详细的错误处理
            print(f"向 API {self.api_url} 发送请求中...")

            # 不需要设置aiohttp.ClientTimeout，直接使用asyncio的超时机制
            if all_tools:
                # 如果有可用工具，则传递工具信息
                if self.debug:
                    print("使用工具调用Claude API")

                # 添加超时参数
                response = await asyncio.wait_for(
                    self.anthropic.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens=1000,
                        messages=messages,
                        tools=all_tools
                    ),
                    timeout=60  # 60秒超时
                )
            else:
                # 如果没有可用工具，则直接调用API
                if self.debug:
                    print("无工具调用Claude API")

                # 添加超时参数
                response = await asyncio.wait_for(
                    self.anthropic.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens=1000,
                        messages=messages
                    ),
                    timeout=60  # 60秒超时
                )

            print("API响应已接收")

            # 处理纯文本回复
            text_parts = []
            for content in response.content:
                if content.type == 'text':
                    text_parts.append(content.text)

            if text_parts:
                text_response = "\n".join(text_parts)
                final_text.append(text_response)

            # 处理工具调用
            if any(content.type == 'tool_use' for content in response.content):
                tool_response = await self._handle_tool_responses(response, messages, all_tools)
                final_text.append(tool_response)

            # 确保返回内容不为空
            if not final_text:
                final_text.append("收到了响应，但没有文本内容可显示。")

        except asyncio.TimeoutError:
            return "API请求超时。请检查您的网络连接并稍后重试。"
        except Exception as e:
            if self.debug:
                import traceback
                traceback.print_exc()
            return f"调用API时发生错误: {str(e)}\n请检查API URL和API密钥是否正确。"

        return "\n".join(final_text)

    async def _handle_tool_responses(self, response, messages, all_tools):
        """处理工具调用响应"""
        result_parts = []

        # 添加助手响应
        assistant_content = []
        for content in response.content:
            assistant_content.append(content)

            if content.type == 'text':
                result_parts.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                tool_id = content.id

                result_parts.append(f"[调用工具 {tool_name}]")

                # 解析服务器名称和实际工具名称
                try:
                    server_name, actual_tool_name = tool_name.split('.', 1)

                    if server_name not in self.sessions:
                        result_parts.append(f"[错误: 找不到服务器 {server_name}]")
                        continue

                    server_data = self.sessions[server_name]
                    session = server_data["session"]

                    # 执行工具调用
                    if self.debug:
                        print(f"调用工具 {actual_tool_name} 参数: {tool_args}")

                    tool_result = await session.call_tool(actual_tool_name, tool_args)
                    tool_result_content = tool_result.content

                    if self.debug:
                        print(f"工具调用结果: {tool_result_content[:100]}...")

                    # 将工具结果添加到结果中
                    result_parts.append(f"[工具 {tool_name} 结果]: {tool_result_content[:100]}...")

                    # 在消息历史中添加助手消息
                    messages.append({
                        "role": "assistant",
                        "content": assistant_content
                    })

                    # 添加工具结果
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": tool_result_content
                            }
                        ]
                    })

                    # 获取对工具结果的回复
                    follow_up_response = self.anthropic.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens=1000,
                        messages=messages
                    )

                    # 添加后续回复到结果中
                    for follow_content in follow_up_response.content:
                        if follow_content.type == 'text':
                            result_parts.append(follow_content.text)

                except Exception as e:
                    if self.debug:
                        import traceback
                        traceback.print_exc()
                    result_parts.append(f"[调用工具 {tool_name} 时出错: {str(e)}]")

        return "\n".join(result_parts)

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n" + "=" * 30)
        print("多MCP客户端已启动!")
        print("=" * 30)

        if not self.sessions:
            print("警告: 没有连接到任何MCP服务器，LLM将不能使用任何工具。")
        else:
            print(
                f"已连接到 {len(self.sessions)} 个MCP服务器，共 {sum(len(s['tools']) for s in self.sessions.values())} 个工具可用")

        print("\n输入您的问题或输入'quit'退出。")

        # 使用 asyncio.Queue 来处理输入和输出
        input_queue = asyncio.Queue()

        # 创建一个单独的任务来读取用户输入
        async def user_input_task():
            while True:
                print("\n问题: ", end="", flush=True)
                query = await asyncio.to_thread(input)  # Python 3.9+ 使用 to_thread
                await input_queue.put(query.strip())
                if query.strip().lower() == 'quit':
                    break

        # 启动用户输入任务
        input_task = asyncio.create_task(user_input_task())

        try:
            while True:
                query = await input_queue.get()

                if query.lower() == 'quit':
                    break

                print("正在处理您的问题，请稍候...")
                try:
                    response = await self.process_query(query)
                    print("\n" + response)
                except Exception as e:
                    print(f"\n错误: {str(e)}")
                    if self.debug:
                        import traceback
                        traceback.print_exc()
        finally:
            # 确保取消输入任务
            input_task.cancel()
            try:
                await input_task
            except asyncio.CancelledError:
                pass
    
    async def cleanup(self):
        """清理资源"""
        if self.debug:
            print("清理资源...")
        await self.exit_stack.aclose()

async def main():
    # 解析命令行参数
    args = parse_arguments()
    
    # 获取配置信息
    api_url = args.api_url
    api_key = args.api_key
    config_path = args.config
    connect_timeout = args.connect_timeout
    debug = args.debug
    
    print("="*50)
    print("多MCP客户端启动中...")
    print("="*50)
    
    # 显示环境和配置信息
    print(f"\n运行环境:")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"配置文件: {config_path}")
    print(f"连接超时: {connect_timeout}秒")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    
    # 初始化服务器管理器
    server_manager = MCPServerManager(config_path, debug=debug)
    
    # 启动所有配置的MCP服务器
    server_processes = server_manager.start_servers()
    
    # 初始化多MCP客户端
    client = MultiMCPClient(
        api_url=api_url, 
        api_key=api_key, 
        config_path=config_path,
        connect_timeout=connect_timeout,
        debug=debug
    )
    
    try:
        # 连接到所有服务器
        await client.connect_to_servers(server_processes)
        
        # 启动聊天循环
        await client.chat_loop()
    except Exception as e:
        print(f"程序运行时出错: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
    finally:
        # 清理客户端资源
        await client.cleanup()
        
        # 停止所有服务器
        server_manager.stop_servers()

if __name__ == "__main__":
    asyncio.run(main()) 