#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ocean Engine Ad Data Calculator (Browser Mode)
Calculates CPF, CPE, CTR metrics and triggers pause/scale decisions.
"""

import sys
import json
from datetime import datetime, timedelta


def calc_metrics(ads_data):
    """Calculate CPF, CPE, CTR for each ad and suggest actions.

    ads_data format: [
        {"name": "Ad-A", "cost": 150.5, "show": 12000, "click": 800,
         "follow": 50, "like": 30, "comment": 10, "share": 5, "budget": 300},
    ]
    Returns: per-ad metrics + action suggestions
    """
    results = []
    totals = {"cost": 0, "show": 0, "click": 0, "follow": 0,
              "like": 0, "comment": 0, "share": 0}

    for ad in ads_data:
        cost = ad.get("cost", 0)
        show = ad.get("show", 0)
        click = ad.get("click", 0)
        follow = ad.get("follow", 0)
        like = ad.get("like", 0)
        comment = ad.get("comment", 0)
        share = ad.get("share", 0)
        budget = ad.get("budget", 0)
        interactions = like + comment + share

        cpk = cost / follow if follow > 0 else (999 if cost > 0 else 0)
        cpe = cost / interactions if interactions > 0 else (999 if cost > 0 else 0)
        ctr = (click / show * 100) if show > 0 else 0
        budget_usage = (cost / budget * 100) if budget > 0 else 0

        # === Pause rules ===
        action = "keep"
        reason = ""
        if cost > 100 and cpk > 0.17:
            action = "pause"
            reason = "CPF={:.3f} > 0.17 (cost={})".format(cpk, cost)
        elif cost > 50 and cpe > 0.009:
            action = "pause"
            reason = "CPE={:.4f} > 0.009 (cost={})".format(cpe, cost)
        elif cost > 150 and follow == 0:
            action = "pause"
            reason = "zero follow (cost={})".format(cost)
        elif ctr < 0.8 and show > 10000:
            action = "pause"
            reason = "CTR={:.2f}% < 0.8% (show={})".format(ctr, show)

        # === Scale rules ===
        scale_action = ""
        if cpk < 0.10 and budget_usage > 80:
            scale_action = "SCALE: budget x1.5 (new={})".format(int(budget * 1.5))
        elif cpe < 0.005:
            scale_action = "SCALE: check 2 consecutive days -> budget x1.5"
        elif ctr > 5:
            scale_action = "SCALE: clone to more ad groups"

        results.append({
            "name": ad["name"],
            "cost": cost,
            "show": show,
            "click": click,
            "follow": follow,
            "interactions": interactions,
            "CPF": round(cpk, 3),
            "CPE": round(cpe, 4),
            "CTR": round(ctr, 2),
            "budget_usage": round(budget_usage, 1),
            "action": action,
            "action_reason": reason,
            "scale_suggest": scale_action,
        })

        for k in totals:
            totals[k] += ad.get(k, 0)

    total_inter = totals["like"] + totals["comment"] + totals["share"]
    summary = {
        "total_cost": totals["cost"],
        "total_show": totals["show"],
        "total_click": totals["click"],
        "total_follow": totals["follow"],
        "total_interactions": total_inter,
        "cpk_overall": round(totals["cost"] / totals["follow"], 3) if totals["follow"] else 0,
        "cpe_overall": round(totals["cost"] / total_inter, 4) if total_inter else 0,
        "ctr_overall": round(totals["click"] / totals["show"] * 100, 2) if totals["show"] else 0,
    }

    return {"summary": summary, "ads": results}


def check_balance_alert(balance, daily_avg_cost):
    """Balance alerts"""
    alerts = []
    if balance < daily_avg_cost * 2:
        alerts.append("[URGENT] Balance < 2 days spend, recharge NOW!")
    elif balance < daily_avg_cost * 3:
        alerts.append("[WARNING] Balance < 3 days spend, recharge suggested")
    if balance < 200:
        alerts.append("[HALT] Balance < 200 RMB, stop creating new ads")
    return alerts


def suggest_new_ad_count(balance):
    """Suggest how many new ads to create based on balance"""
    if balance >= 1000:
        return 4, "Balance OK, suggest creating 4 ads"
    elif balance >= 500:
        return 3, "Balance moderate, suggest creating 3 ads"
    elif balance >= 200:
        return 2, "Balance low, suggest creating 2 ads"
    else:
        return 0, "Balance too low, do NOT create new ads"


def print_report(calc_result, balance=None, daily_avg=None):
    """Print formatted report"""
    s = calc_result["summary"]
    ads = calc_result["ads"]

    print("=" * 60)
    print("  Ocean Engine Ad Analysis  {}".format(datetime.now().strftime('%Y-%m-%d')))
    print("=" * 60)
    print()
    print("[Summary]")
    print("  Spend:      RMB {:.2f}".format(s['total_cost']))
    print("  Impressions:{}  (CTR: {:.2f}%)".format(s['total_show'], s['ctr_overall']))
    print("  Clicks:     {}".format(s['total_click']))
    print("  New Follows:{}  (CPF: {:.3f})".format(s['total_follow'], s['cpk_overall']))
    print("  Interactions:{} (CPE: {:.4f})".format(s['total_interactions'], s['cpe_overall']))

    if balance and daily_avg:
        alerts = check_balance_alert(balance, daily_avg)
        if alerts:
            print()
            print("[Balance Alerts]")
            for a in alerts:
                print("  {}".format(a))

    print()
    print("[Ad Details]")
    header = "  {:<20} {:>8} {:>8} {:>8} {:>6} {:>6}".format(
        'Name', 'Cost', 'CPF', 'CPE', 'CTR', 'Action')
    print(header)
    print("  " + "-" * 56)
    for ad in ads:
        icon = "STOP" if ad["action"] == "pause" else "OK"
        line = "  {:<20} {:>8.2f} {:>8.3f} {:>8.4f} {:>5.2f}% {:>6}".format(
            ad['name'], ad['cost'], ad['CPF'], ad['CPE'], ad['CTR'], icon)
        print(line)
        if ad["action_reason"]:
            print("    -> {}".format(ad["action_reason"]))
        if ad["scale_suggest"]:
            print("    + {}".format(ad["scale_suggest"]))

    if balance:
        count, tip = suggest_new_ad_count(balance)
        print()
        print("[New Ads] {}".format(tip))

    return s, ads


def main():
    """CLI entry: read JSON data from stdin"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: pipe ad data JSON via stdin")
        print('Example: type data.json | python calc_metrics.py')
        print()
        print("JSON format:")
        print('[{"name":"Ad-A","cost":100,"show":5000,"click":200,')
        print('  "follow":20,"like":15,"comment":5,"share":3,"budget":300}]')
        return

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            print("Pipe JSON data via stdin, or use --help")
            return
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print("JSON parse error: {}".format(e))
        return

    result = calc_metrics(data)
    balance = None
    daily_avg = None
    if len(sys.argv) >= 3:
        balance = float(sys.argv[1])
        daily_avg = float(sys.argv[2])

    print_report(result, balance, daily_avg)

    if "--json" in sys.argv:
        print("\n--- JSON OUTPUT ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()