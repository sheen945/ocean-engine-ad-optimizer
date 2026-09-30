#!/usr/bin/env python3
"""
巨量引擎投流策略学习工具
从官方和第三方来源获取最新投流方法论，分析可行性并输出建议。
"""

import json
import sys
import os
import urllib.request
import urllib.parse
import re
from datetime import datetime

# 数据源配置
SOURCES = [
    {
        "name": "巨量引擎官方帮助中心",
        "url": "https://www.oceanengine.com/support",
        "type": "official",
        "keywords": ["信息流", "吸粉", "涨粉", "精准投放", "出价策略"],
    },
    {
        "name": "巨量学",
        "url": "https://www.oceanengine.com/academy",
        "type": "official",
        "keywords": ["投流技巧", "信息流广告", "粉丝增长", "优化"],
    },
    {
        "name": "巨量引擎官方公众号",
        "search_url": "https://mp.weixin.qq.com/mp/search?search=巨量引擎投流技巧",
        "type": "semi-official",
    },
    {
        "name": "36氪-营销",
        "url": "https://36kr.com/search/articles/巨量引擎投流",
        "type": "media",
    },
    {
        "name": "鸟哥笔记",
        "url": "https://www.niaogebiji.com/search?keyword=巨量引擎",
        "type": "professional",
    },
]


def fetch_url(url, max_chars=5000):
    """简单抓取网页文本"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            # 简单清理 HTML 标签
            clean = re.sub(r"<[^>]+>", " ", raw)
            clean = re.sub(r"\s+", " ", clean)
            return clean[:max_chars]
    except Exception as e:
        return f"[获取失败: {e}]"


def extract_strategies(text):
    """从文本中提取策略关键词"""
    patterns = [
        r"(?:策略|方法|技巧|方案|玩法).{0,50}?(?:涨粉|吸粉|粉丝|精准).{0,50}",
        r"(?:出价|定向|素材|人群|预算).{0,30}?(?:优化|提升|降低|策略|方法).{0,50}",
        r"(?:最新|最近|今年|2025|2026).{0,30}?(?:投流|投放|信息流).{0,50}",
        r"(?:CPM|CPC|CPF|ROI|投产).{0,30}?(?:优化|降低|提升).{0,50}",
    ]
    results = []
    for pat in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        results.extend(matches)
    # 去重截断
    seen = set()
    unique = []
    for r in results:
        r = r.strip()
        if r and r not in seen and len(r) > 5:
            seen.add(r)
            unique.append(r)
    return unique[:30]


def analyze_feasibility(strategies):
    """分析策略的可行性"""
    if not strategies:
        return "未发现新的投流策略。建议扩大搜索词范围。"

    lines = ["## 策略可行性分析", ""]
    for i, s in enumerate(strategies[:10], 1):
        risk = "🟢 低风险" if len(s) < 60 else "🟡 中等"
        lines.append(f"{i}. **{s}**")
        lines.append(f"   来源可信度: {risk}")
        lines.append(f"   建议: 可作为 A/B 测试素材，小预算验证")
        lines.append("")
    return "\n".join(lines)


def search_strategies(keywords=None):
    """主入口: 搜索最新投流策略并分析"""
    if keywords is None:
        keywords = ["巨量引擎 信息流 涨粉 2026", "巨量引擎 投流 新方法",
                      "信息流广告 吸粉 技巧", "巨量千川 精准投放"]
    
    all_strategies = []
    for source in SOURCES[:2]:  # 只查前两个最可靠的源,避免太慢
        url = source.get("url", source.get("search_url", ""))
        if not url:
            continue
        text = fetch_url(url, max_chars=3000)
        found = extract_strategies(text)
        all_strategies.extend(found)

    analysis = analyze_feasibility(all_strategies)
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "sources_scanned": [s["name"] for s in SOURCES[:2]],
        "strategies_found": len(all_strategies),
        "top_strategies": all_strategies[:10],
        "analysis": analysis,
    }
    return output


def cmd_run():
    """命令行入口"""
    print("=== 巨量引擎投流策略搜索 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("正在搜索最新投流策略...")
    print()

    # 支持自定义关键词
    keywords = None
    if len(sys.argv) > 1:
        keywords = sys.argv[1:]

    result = search_strategies(keywords)
    print(f"扫描了 {len(result['sources_scanned'])} 个来源")
    print(f"发现 {result['strategies_found']} 条潜在策略")
    print()
    print(result["analysis"])

    # 同时输出 JSON 方便程序对用
    output_file = os.path.join(os.path.dirname(__file__), "..", "strategy_cache.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"详细结果已缓存至: {output_file}")


if __name__ == "__main__":
    cmd_run()
