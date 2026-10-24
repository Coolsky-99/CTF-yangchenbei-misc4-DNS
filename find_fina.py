import json
import re
import datetime

log_file = 'orchestration_logs.json' 
target_emp = 'EMP_199' 

print(f"🕵️‍♂️ 正在深度审计 {target_emp} 及全局异常...\n")


dns_records = []
git_writes = []
read_files_by_199 = []
install_time = None

with open(log_file, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            data = json.loads(line.strip())
            tool = data.get("tool")
            emp = data.get("employee_id")
            args = data.get("args", {})
            ts = data.get("timestamp") # 假设有时间戳字段

            # 1. 找恶意组件的安装时间 (问题 4)
            # 寻找执行 npx 或者 install 命令的日志
            if tool in ["execute_command", "bash", "terminal"]:
                cmd = args.get("command", "")
                if "mcp-wiki" in cmd or "npm" in cmd or "npx" in cmd:
                    # 转换时间戳格式 YYYYMMDDHHMM
                    if ts:
                        # 假设 ts 是毫秒时间戳，如果是秒则不需要除1000
                        dt = datetime.datetime.fromtimestamp(int(ts)/1000) 
                        time_str = dt.strftime('%Y%m%d%H%M')
                        print(f" [疑似安装时间] 行号: {line_num}, 员工: {emp}")
                        print(f"时间: {time_str}, 命令: {cmd}\n")

            # 2. 找被篡改的 Git 配置 (问题 6)
            if tool == "write_file":
                path = args.get("path", "")
                content = args.get("content", "")
                if ".git/config" in path or ".gitconfig" in path:
                    print(f" [发现 Git 配置篡改] 行号: {line_num}, 员工: {emp}")
                    print(f"写入内容: {content}\n")

            # 3. 收集 DNS 记录，准备解码 (问题 1 和 2)
            if tool == "dns_query":
                query = args.get("query", "")
                if query:
                    dns_records.append((line_num, query))

            # 4. 看 EMP_199 读了什么越权文档 (问题 5)
            if tool == "read_file" and emp == target_emp:
                read_files_by_199.append(args.get("path"))
            
            # 5. 直接找带 glpat 或 ghp 的 Token
            arg_str = json.dumps(data)
            if "glpat-" in arg_str or "ghp_" in arg_str:
                print(f" [发现疑似 Token 明文] 行号: {line_num}")
                print(f"内容: {arg_str[:500]}\n")

        except Exception as e:
            pass

# 打印 EMP_199 读过的文件
print(f"\n [{target_emp} 越权读取的文件] (问题5可能在这):")
for f_path in set(read_files_by_199):
    print(f" - {f_path}")

# 打印所有 DNS 请求，看看哪个像隧道
print(f"\n [全局 DNS 查询记录 (看哪个像隧道)]:")
domain_counts = {}
for line_num, q in dns_records:
    # 提取根域名（简单逻辑）
    parts = q.split('.')
    if len(parts) >= 2:
        root = '.'.join(parts[-2:])
        domain_counts[root] = domain_counts.get(root, 0) + 1

for d, count in domain_counts.items():
    if "vimxmx" not in d and "jira" not in d:
        print(f" - {d} (出现 {count} 次)")
        # 如果出现次数多，打印出几个子域名看看
        if count > 5:
            subdomains = [q for _, q in dns_records if d in q][:5]
            print(f"    示例: {subdomains}")