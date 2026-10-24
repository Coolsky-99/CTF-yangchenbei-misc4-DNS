import json
import re
from collections import Counter

# 替换为你真实的文件名
log_file = 'orchestration_logs.json' 

print("🚀 开始扫描日志，请稍候...\n")

suspicious_domains = []
written_files = []
read_files = []
employee_actions = Counter()

with open(log_file, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            data = json.loads(line.strip())
            
            # 记录员工活跃度
            emp = data.get("employee_id")
            if emp:
                employee_actions[emp] += 1

            # 寻找 1 和 6 的线索：异常的域名和 DNS
            if data.get("tool") in ["dns_query", "http_request", "web_search"]:
                args_str = json.dumps(data.get("args", {}))
                # 匹配域名
                domains = re.findall(r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}', args_str)
                for d in domains:
                    if "vimxmx.internal" not in d and "npmjs.org" not in d and "jira" not in d:
                        suspicious_domains.append((d, line_num))

            # 寻找 2 和 4 的线索：写入的配置文件
            if data.get("tool") == "write_file":
                args = data.get("args", {})
                path = args.get("path", "")
                content = args.get("content", "")
                written_files.append((path, content, emp, line_num))
                # 如果看到 mcp 或 git 相关的写入，直接高亮打印
                if "mcp" in path or "git" in path or "ssh" in path:
                    print(f"🚨 [疑似恶意配置写入] 行号: {line_num} | 员工: {emp}")
                    print(f"路径: {path}")
                    print(f"内容: {content[:200]}...\n")

            # 寻找 5 的线索：读取了哪些敏感文档
            if data.get("tool") == "read_file":
                path = data.get("args", {}).get("path", "")
                read_files.append((path, emp, line_num))

        except Exception as e:
            pass # 忽略解析错误的行

print("="*50)
print("🌐 [线索 1/6] 可疑域名 (排除了正常办公域名):")
domain_counts = Counter([d[0] for d in suspicious_domains])
for d, count in domain_counts.most_common(10):
    print(f" - {d} (出现 {count} 次)")

print("\n📄 [线索 5] 被读取的所有文档 (重点看敏感目录，如 .git, .ssh, 含有密码的 md):")
unique_reads = set([r[0] for r in read_files])
for r in unique_reads:
    print(f" - {r}")

print("\n👤 [线索 3] 最活跃/最可疑的员工 (操作数最多):")
for emp, count in employee_actions.most_common(5):
    print(f" - {emp} (操作了 {count} 次)")