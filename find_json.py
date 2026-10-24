import json
import re
import datetime

log_file = 'orchestration_logs.json' 

print("🚀 正在生成六位一体终极报告...\n")

with open(log_file, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            data = json.loads(line.strip())
            tool = data.get("tool")
            emp = data.get("employee_id")
            args = data.get("args", {})
            ts = data.get("timestamp")
            
            # ========== 找问题 4：安装时间 (针对行号 37538 附近) ==========
            if line_num == 37538 and ts:
                # 假设时间戳是毫秒
                dt = datetime.datetime.fromtimestamp(ts/1000)
                print(f"🎯 [问题4-安装时间]: {dt.strftime('%Y%m%d%H%M')}")

            # ========== 找问题 2：被盗凭据 (Token 明文) ==========
            # 如果 token 被隐藏在 content 或者命令行里，用正则揪出来
            full_str = json.dumps(data)
            tokens = re.findall(r'(glpat-[a-zA-Z0-9\-]+|ghp_[a-zA-Z0-9]+)', full_str)
            if tokens:
                print(f"🎯 [问题2-被盗凭据]: {tokens[0]} (行号: {line_num})")

            # ========== 找问题 5：越权读取的文档 ==========
            # 看 EMP_199 到底读了哪个包含敏感信息的文档
            if emp == 'EMP_199' and tool == 'read_file':
                path = args.get('path', '')
                # 过滤掉源代码文件，找 txt, md, pdf, docx 等
                if any(path.endswith(ext) for ext in ['.md', '.txt', '.pdf', '.docx']):
                    print(f"🎯 [问题5-越权文档]: {path.split('/')[-1]} (行号: {line_num})")

            # ========== 找问题 1 和 6：恶意域名 ==========
            # 找网络请求中的非正常域名
            if tool in ["http_request", "dns_query", "execute_command"]:
                domains = re.findall(r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}', json.dumps(args))
                for d in domains:
                    if "vimxmx" not in d and "jira" not in d and "npmjs" not in d:
                        print(f"🎯 [发现可疑域名]: {d} (行号: {line_num})")

        except Exception as e:
            pass