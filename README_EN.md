# ocean-engine-ad-optimizer

> An intelligent Ocean Engine (巨量引擎) feed-ad optimization skill (browser mode) — no API required. It automates the entire daily ad-ops loop through browser automation: creating new ads, pausing underperformers, monitoring balance, daily reporting, and continuously learning and validating new buying strategies.

## Introduction

This is an Agent Skill for WorkBuddy / Claude Code. It lets your AI assistant log into the Ocean Engine ad platform via browser automation and take over the daily operations of feed advertising: checking account balance, pulling yesterday's report, pausing bad ads against hard cost lines, deciding how many new ads to create based on spend velocity, producing a daily recap report, and continuously learning the latest media-buying methodologies from official and industry sources — validated through small-budget experiments.

It is designed for individual media buyers, content creators, and SMB advertisers who have login access to the Ocean Engine console but cannot obtain a Marketing API credential. Core optimization targets: **CPF (cost per follower) < ¥0.17, CPE (cost per engagement) < ¥0.009**.

**Trigger keywords**: 巨量引擎, 信息流广告, 投流, 涨粉, 吸粉, 千川, CPF, CPE, 广告优化, 投放优化, ocean engine, 巨量广告.

## Features

- **Balance monitoring & alerts**: checks account balance before every run; warns when balance < 1.5× the 3-day average daily spend, escalates and pauses ad creation below 2×, and stops creating new ads entirely below ¥200.
- **Cost-guarantee-aware pause logic**: before pausing any ad, the skill reads the "cost guarantee" (平台赔付) status column. Ads still inside the guarantee window with ≥20% cost overrun are kept running to collect the platform rebate, while ads past the window face hard red lines (e.g. spend > ¥100 with CPF > 0.17 → pause immediately).
- **Smart ad creation**: decides how many new ads to build each day (0–6) from a spend-velocity × balance matrix, then drives the browser through targeting, bidding (target CPF × 1.3), creative upload, and review submission.
- **Scale-up decisions**: budget ×1.5 when CPF < 0.10 near the daily cap (up to ¥5,000); consider duplicating the ad group when CTR > 5%, so winning plans get room to run.
- **Standardized daily report**: built-in recap template covering spend/CPF/CPE/CTR, rebate arrivals, every pause/create/budget action, days of budget remaining, and trend analysis.
- **Strategy learning & experimentation loop**: `scripts/strategy_scraper.py` pulls the latest methodologies from the Ocean Engine help center, 巨量学, 36kr, 鸟哥笔记 and more, tags source credibility, and recommends experiments. Experiments follow a rigorous framework: one proven control ad, one experimental ad, 3 days or ¥200 of observation, and adoption only if CPF improves by 15%+ with statistical significance.
- **Automated metrics**: `scripts/ad_operations.py` computes CPF/CPE/CTR from spend, impressions, clicks, follows, and engagements, then suggests pause/scale actions.

## How It Works / Tech Stack

- **Form factor**: a WorkBuddy / Claude Code Agent Skill (declarative `SKILL.md` + references + scripts).
- **Browser automation**: all web operations go through the `chrome-browser` skill (Google Chrome + CDP debug port 9222 + a fixed login-profile directory `chrome-cdp-profile`). The login session is maintained by the system browser — the skill never stores usernames or passwords.
- **Scripts**: pure Python 3 standard library (`urllib`, `json`, `re`) — no third-party dependencies.
- **Rule documents**: `references/optimization_rules.md` holds the full cost red lines and rebate math; `references/web_guide.md` holds navigation paths for every page of the Ocean Engine console.

Daily execution flow:

```
1. Check balance -> alert and skip creation if low
2. Open Promotions -> screenshot the active ad list
3. Open Reports -> pull yesterday's per-ad data
4. Apply pause rules ad by ad (check rebate status first)
5. Decide creation count from balance & spend velocity -> build ads in the browser
6. Run the strategy-learning script
7. Produce the daily recap report
8. Summarize actions and anomalies for the user
```

## Installation & Usage

Copy this repository into your skills directory, keeping the folder name `ocean-engine-ad-optimizer`:

- WorkBuddy / CodeBuddy: `~/.workbuddy/skills/ocean-engine-ad-optimizer/`
- Claude Code: `~/.claude/skills/ocean-engine-ad-optimizer/`

Restart the session, then simply mention a trigger keyword (e.g. "巨量引擎", "投流", "CPF") to activate the skill.

**Prerequisites on first use**:

1. Log into `https://ad.oceanengine.com/` or `https://qianchuan.jinritemai.com/` in the system Chrome browser and confirm you can reach the ad management console.
2. Confirm the account name/ID, current balance, and goal (follower growth / engagement; default: follower growth with CPF < 0.17).

The strategy-learning script can also be run standalone:

```bash
python scripts/strategy_scraper.py
```

## Project Structure

```
ocean-engine-ad-optimizer/
├── SKILL.md                        # Skill definition (metadata + full operating spec)
├── README.md                       # Chinese README
├── README_EN.md                    # This file
├── scripts/
│   ├── ad_operations.py            # CPF/CPE/CTR calculation + pause/scale suggestions
│   └── strategy_scraper.py         # Media-buying methodology scraping & analysis
└── references/
    ├── optimization_rules.md       # Cost red lines, rebate rules, targeting strategies
    └── web_guide.md                # Navigation paths for the Ocean Engine console
```

## Notes

- Requires the `chrome-browser` skill installed on the machine; keep browser actions at least 2 seconds apart to avoid anti-bot triggers.
- On CAPTCHAs, sliders, or pop-ups: pause immediately, take a screenshot, and notify the user — never handle them silently.
- **During the rebate window, do not change bids or targeting (max 2 changes each per day), do not pause, and do not enable auto-boost — any of these voids the rebate.**
- Never inflate costs on purpose to farm rebates — rebates exceeding 50% of real cash spend trigger platform risk control.
- Ask the user to confirm targeting and budget before submitting any new ad; learned strategies require human review before entering production.
- The skill stores no credentials; the login session lives entirely in the local browser profile.

## License

MIT

## Author

sheen945
