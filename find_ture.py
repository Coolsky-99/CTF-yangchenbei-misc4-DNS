import json
import re

log_file = 'orchestration_logs.json' 

print("🔍 正在追踪核心恶意行为...\n")

with open(log_file, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            data = json.loads(line.strip())
            tool = data.get("tool")
            emp = data.get("employee_id")
            args = data.get("args", {})
            
            # 1. 抓取写入 mcp_servers.json 的操作（很可能藏着被盗凭据）
            if tool == "write_file" and "mcp" in args.get("path", ""):
                print(f"🚨 [发现恶意配置写入] 行号: {line_num}, 员工: {emp}")
                print(f"路径: {args.get('path')}")
                print(f"完整内容: {args.get('content')}\n")
            
            # 2. 抓取命令行执行记录（找安装时间、Git篡改）
            if tool == "execute_command" or tool == "bash":
                cmd = args.get("command", "")
                print(f"💻 [命令执行] 行号: {line_num}, 员工: {emp}")
                print(f"命令: {cmd}\n")
            
            # 3. 抓取 HTTP 请求或 DNS 查询（找恶意域名）
            if tool == "http_request" or tool == "dns_query":
                arg_str = json.dumps(args)
                # 找域名
                domains = re.findall(r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}', arg_str)
                for d in domains:
                    if "vimxmx.internal" not in d and "npmjs" not in d and "jira" not in d:
                        print(f"🌐 [可疑网络请求] 行号: {line_num}, 员工: {emp}")
                        print(f"内容: {arg_str}\n")

        except Exception as e:
            pass