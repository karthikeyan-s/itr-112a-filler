# ITR Schedule 112A Filler (Skill & Source Tool)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

An AI Agent Skill and Python toolkit for parsing capital gains statements (CAMS, KFintech, Demat/Depository, Broker reports) and generating the filled **Schedule 112A CSV** for India's Income Tax Return (ITR-2 / ITR-3).

---

## 📌 Overview

Section 112A of the Indian Income Tax Act taxes Long-Term Capital Gains (LTCG) on listed equity shares and equity-oriented mutual fund units where Securities Transaction Tax (STT) was paid.

Filling Schedule 112A requires:
1. **Grandfathering computation (Section 55(2)(ac))** for units acquired on or before **31-Jan-2018** (lot-by-lot classification `BE`).
2. **Consolidation / Entry** for units acquired after **31-Jan-2018** (classification `AE`).
3. **14-column exact schema mapping** matching the official Income Tax Department offline utility requirements.
4. **Schedule CG Item F quarter-wise capital gains split** for advance tax computation.
5. **Reconciliation against AIS (Annual Information Statement)** (SFT-17 / SFT-18).

---

## 📂 Repository Structure

```text
itr-112a-filler/
├── SKILL.md                  # Complete Agent Skill definition (Claude Code / Antigravity / Cursor)
├── scripts/
│   ├── grandfather.py        # Grandfathering arithmetic & 14-column generation
│   ├── quarter_split.py      # Quarter-wise LTCG split for Schedule CG Item F
│   └── validate.py           # 3-way validation & AIS reconciliation helpers
├── references/
│   ├── ais-reconciliation.md # AIS reconciliation patterns & SFT codes
│   ├── csv-format.md         # Schema rules & CSV byte-level formatting constraints
│   ├── depository-mf.md      # Demat mutual funds (NJ-Funds, CDSL/NSDL broker route)
│   ├── equity-brokers.md     # Broker statements (Zerodha, Groww, ICICI Direct, etc.)
│   ├── mutual-funds.md       # RTA statements (CAMS & KFintech parsing)
│   └── quarter-wise-cg.md    # Quarter breakdown rules for FY 2024-25 / 2025-26
├── .gitignore                # Protects sensitive financial data (*.xlsx, *.pdf, *.csv)
├── requirements.txt          # Python dependencies
└── LICENSE                   # MIT License
```

---

## 🚀 Getting Started

### 1. Using as an AI Coding Assistant Skill

This repository contains a full `SKILL.md` designed for AI agents (Claude Code, Antigravity, Cursor):

- **Claude Code**: Place inside your project's `.claude/skills/itr-112a-filler/` or load it directly in your workspace.
- **Antigravity**: Copy to `.agents/skills/itr-112a-filler/` or your global config `~/.gemini/config/skills/itr-112a-filler/`.

When asking your agent to fill Schedule 112A, simply provide your statement files and say:
> *"Fill Schedule 112A using the uploaded CAMS statement and Zerodha tax P&L."*

### 2. Standalone Python Scripts

You can run self-tests and calculation helpers directly:

```bash
# Run grandfathering formula self-test
python scripts/grandfather.py

# Run quarter-wise split self-test
python scripts/quarter_split.py
```

---

## 📊 Schedule 112A Column Specification

| Col # | Field Name | Description |
|---|---|---|
| **1a** | Section Type | `BE` (Acquired on or before 31-Jan-2018) or `AE` (Acquired after 31-Jan-2018) |
| **2** | ISIN Code | 12-character alphanumeric (or `INNOTREQUIRD` for AE consolidated) |
| **3** | Share/Unit Name | Alphanumeric and spaces only |
| **4** | No. of Shares/Units | Number of units sold |
| **5** | Sale-price per Share/Unit | Full Value Consideration per unit |
| **6** | Full Value Consideration (FVC) | Total sale value (rounded to nearest Rupee) |
| **7** | Cost of Acquisition without indexation | Higher of (Cost, Lower of FVC & FMV as of 31-Jan-2018) |
| **8** | Cost of Acquisition | Original purchase cost |
| **9** | Lower of 6 & 11 | Lower of Full Value Consideration and Total FMV |
| **10** | FMV per share/unit as on 31-Jan-2018 | Fair Market Value on cutoff date |
| **11** | Total Fair Market Value | `Col 4 × Col 10` (rounded to nearest Rupee) |
| **12** | Expenditure wholly & exclusively | Transfer expenses / brokerage / STT (if applicable) |
| **13** | Total Deductions | `Col 7 + Col 12` |
| **14** | Balance / Gain | `Col 6 - Col 13` |

---

## 🔒 Privacy & Financial Data Security

- **Strict `.gitignore`**: All personal financial files (`*.xlsx`, `*.xls`, `*.pdf`, `*.csv`) are excluded by default so you never risk committing confidential taxpayer information.
- Always inspect output CSV files before uploading to the Income Tax Portal.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
