from typing import Any
import httpx
import csv
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("tasklist")
    

@mcp.tool()
async def get_tasklist(category: str) -> str:
    """
    根据分类获取任务列表
    
    Args:
        category: 任务分类 (Work, Personal, Fitness, Learning 等)
        
    Returns:
        str: 该分类的任务列表
    Raises:
        ValueError: 无效的任务分类或文件不存在
    """
    # 获取CSV文件的绝对路径
    csv_path = os.path.join(os.path.dirname(__file__), 'task.csv')
    
    # 检查文件是否存在
    if not os.path.exists(csv_path):
        raise ValueError(f"Task file not found: {csv_path}")
    
    tasks = []
    
    # 读取CSV文件
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if category.lower() == 'all' or row['Category'].lower() == category.lower():
                task_info = f"{row['Task Name']} - {row['Description']} (Due: {row['Due Date']}, Priority: {row['Priority']}, Status: {row['Status']})"
                tasks.append(task_info)
    
    if not tasks and category.lower() != 'all':
        return f"No tasks found for category: {category}"
    
    # 格式化输出
    result = f"Tasks for category '{category}':\n" + "\n".join(tasks)
    return result


if __name__ == "__main__":
    # Initialize and run the server
    print('Tasklist server started')
    mcp.run(transport='stdio')
    