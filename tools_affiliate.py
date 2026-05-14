# tools_affiliate.py
# 将 affiliate-links.json 中的联盟链接合并到 tools.json
# 使用方式: python tools_affiliate.py
# 可在 GitHub Actions 中自动运行（每天一次）
#
# 逻辑：
# 1. 读取 affiliate-links.json
# 2. 读取 tools.json
# 3. 对于每个工具：如果 affiliate-links 中有 active 的链接 → 替换 URL
# 4. 如果有 affUrl 但状态为 pending → 添加 ?ref=linkcn 参数（通用追踪）
# 5. 输出 updated_tools.json
#
# 注意：此脚本不修改原始 tools.json，输出为 updated_tools.json
# 合并后的文件需人工审核或设置白名单后才推送到生产环境

import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AFFILIATE_FILE = os.path.join(SCRIPT_DIR, 'affiliate-links.json')
TOOLS_FILE = os.path.join(SCRIPT_DIR, 'tools.json')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'updated_tools.json')

REF_PARAM = "?ref=linkcn"  # 通用追踪参数
REF_PARAM_AFF = "&ref=linkcn"  # 已有QueryString时的追加


def load_json(path, description):
    if not os.path.exists(path):
        print(f"⚠️  文件不存在: {path} — {description}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {path} — {e}")
            return {}


def merge_affiliate_links():
    print(f"=== Link.cn 联盟链接合并工具 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    affiliates = load_json(AFFILIATE_FILE, "联盟配置表")
    tools = load_json(TOOLS_FILE, "工具数据")

    if isinstance(affiliates, dict):
        affiliate_map = affiliates  # 是字典格式
    elif isinstance(affiliates, list):
        # 兼容列表格式
        affiliate_map = {item['id']: item for item in affiliates if 'id' in item}
    else:
        affiliate_map = {}

    updated_count = 0
    active_aff_count = 0
    pending_aff_count = 0

    for tool in tools:
        tool_id = tool.get('id', '')
        aff = affiliate_map.get(tool_id)

        if not aff:
            continue

        status = aff.get('status', 'direct')
        aff_url = aff.get('affiliate_url', '').strip()
        original_url = tool.get('url', '')
        new_url = original_url

        if status == 'active' and aff_url:
            # 联盟已激活，优先使用联盟链接
            new_url = aff_url
            active_aff_count += 1
            tool['_affiliate'] = {
                'program': aff.get('program', ''),
                'commission': aff.get('commission', ''),
                'status': 'active'
            }
            print(f"  ✅ [{tool_id}] {tool.get('title')} → 联盟链接 (佣金: {aff.get('commission', 'N/A')})")

        elif status == 'pending' and aff_url:
            # 已申请但未审批，添加追踪参数
            separator = '&' if '?' in original_url else '?'
            new_url = original_url + separator + 'via=linkcn'
            pending_aff_count += 1
            tool['_affiliate'] = {
                'program': aff.get('program', ''),
                'commission': aff.get('commission', ''),
                'status': 'pending'
            }
            print(f"  ⏳ [{tool_id}] {tool.get('title')} → 追踪参数已添加 (等待联盟审批)")

        elif status == 'direct' or not aff_url:
            # 无联盟计划，保持直链，添加通用追踪参数
            if original_url and original_url != 'https://tool.link.cn':
                separator = '&' if '?' in original_url else '?'
                new_url = original_url + separator + 'via=linkcn'
            tool['_affiliate'] = {'status': 'direct', 'note': aff.get('note', '')}

        if new_url != original_url:
            tool['url'] = new_url
            updated_count += 1

    # 统计
    total_tools = len([t for t in tools if t.get('id') not in ('SYNC-INFO', 'STATUS')])
    print()
    print(f"=== 统计结果 ===")
    print(f"工具总数: {total_tools}")
    print(f"使用联盟链接: {active_aff_count}")
    print(f"添加追踪参数: {pending_aff_count}")
    print(f"无变化: {total_tools - active_aff_count - pending_aff_count}")
    print(f"总计更新: {updated_count}")

    # 输出
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=4, ensure_ascii=False)

    print()
    print(f"已输出到: {OUTPUT_FILE}")
    print()
    print("💡 提示: 请审核 updated_tools.json 后手动替换 tools.json")
    print("   联盟审批通过后，将 affiliate-links.json 中对应工具的 status 改为 'active'")

    return tools


if __name__ == '__main__':
    merge_affiliate_links()
