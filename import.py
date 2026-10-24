import json
import datetime

log_file = 'orchestration_logs.json'
target_emp = 'EMP_107'

print(f"🕵️‍♂️ 正在提取 {target_emp} 的所有操作轨迹...\n")

# 用于统计该员工使用了哪些工具
tool_stats = {}

with open(log_file, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        try:
            data = json.loads(line.strip())
            
            # 核心过滤：只找目标员工的数据
            if data.get("employee_id") == target_emp:
                tool = data.get("tool", "对话/无工具")
                tool_stats[tool] = tool_stats.get(tool, 0) + 1
                
                # 提取时间（如果存在）
                ts = data.get("timestamp")
                time_str = ""
                if ts:
                    try:
                        dt = datetime.datetime.fromtimestamp(ts/1000)
                        time_str = f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] "
                    except:
                        pass
                
                # 提取 Agent 的回复（看看有没有被忽悠）
                llm_response = data.get("llm_response", "")
                
                # 提取工具调用的参数
                args = data.get("args", {})
                
                # 判断是否是高危操作，如果是，加点颜色（文字高亮）
                if tool in ["write_file", "execute_command", "dns_query"]:
                    print(f"🚨 行号: {line_num} {time_str} [高危操作: {tool}]")
                    print(f"   参数: {json.dumps(args, ensure_ascii=False)[:300]}")
                    if llm_response:
                        print(f"   Agent回复: {llm_response[:100]}")
                    print("-" * 50)
                    
        except Exception:
            pass

print("\n📊 ===== 员工行为特征统计 =====")
for t, count in sorted(tool_stats.items(), key=lambda x: x[1], reverse=True):
    print(f" - {t}: {count} 次")

print("\n💡 提示：如果高危操作太多，你可以修改代码中的判断条件，例如只看 'dns_query' 或 'write_file'。")