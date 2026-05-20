# DABstep Dataset Analysis

> **Data Agent Benchmark for Multi-step Reasoning** by Adyen + HuggingFace
> 450 tasks | 72 easy, 378 hard | All tasks share the same 7 data files

---

## Executive Summary

DABstep is a benchmark for evaluating AI agents on payment data analysis tasks. All 450 tasks operate on the same underlying dataset of ~138K payment transactions with associated fee rules, merchant data, and documentation. Tasks range from simple data exploration (counting transactions, computing averages) to complex multi-step fee calculations requiring cross-referencing 3+ data files and applying counterfactual reasoning.

**Key findings:**
- **84% of tasks (378) are "hard"** — all require fee-related reasoning
- **16% of tasks (72) are "easy"** — basic data exploration on payments.csv
- **74% of all tasks (334) involve fee calculations** — this is overwhelmingly a fee-reasoning benchmark
- Tasks are heavily templated — many categories are parametric variations of the same question pattern
- The most common answer format is a single number (44%), followed by strings (25%) and comma-separated lists (24%)

---

## Summary Table

| # | Category | Count | Easy | Hard | Answer Format | Data Sources | Complexity |
|---|----------|-------|------|------|---------------|--------------|------------|
| 1 | Fee Calc: Average Fee by Card Scheme | 60 | 0 | 60 | Number (6 dec) | fees.json | Multi-step: iterate all fees per scheme, compute average |
| 2 | Fee Lookup: Applicable Fees for Merchant | 45 | 0 | 45 | Comma-sep list | fees.json + payments.csv + merchant_data.json | Multi-step: match merchant → fee rules by day/month |
| 3 | Fee Calc: Total Fees for Merchant | 45 | 0 | 45 | Number (2 dec) | fees.json + payments.csv + merchant_data.json | Multi-step: match transactions → applicable fees → sum |
| 4 | Counterfactual: Relative Fee Change | 40 | 0 | 40 | Number (6 dec) | fees.json + payments.csv + merchant_data.json | Multi-step: compute fees under altered fee rules |
| 5 | Fee Optimization: Steer Traffic | 30 | 0 | 30 | String | fees.json + payments.csv + merchant_data.json | Multi-step: compute fees per scheme, find min/max |
| 6 | Counterfactual: Preferred ACI | 25 | 0 | 25 | String (letter) | fees.json + payments.csv | Multi-step: test ACI alternatives for fraud txns |
| 7 | Aggregation: Average by Group | 20 | 0 | 20 | Grouped list | payments.csv | Multi-step: filter + groupby + sort |
| 8 | Fee Comparison: Most Expensive ACI | 20 | 0 | 20 | String (letter) | fees.json | Multi-step: compute fees per ACI, compare |
| 9 | Fee Lookup: Fee IDs by Conditions | 20 | 0 | 20 | Comma-sep list | fees.json | Multi-step: filter fees.json by account_type + aci |
| 10 | Counterfactual: MCC Code Change | 20 | 0 | 20 | Number (6 dec) | fees.json + payments.csv + merchant_data.json + MCC codes | Multi-step: recompute fees with altered MCC |
| 11 | Counterfactual: Fee Scenario | 20 | 0 | 20 | Number / list | fees.json + payments.csv + merchant_data.json | Multi-step: what-if fee rule modifications |
| 12 | Ranking: Top/Highest | 13 | 13 | 0 | String / Number | payments.csv | 1-2 step: sort + pick |
| 13 | Aggregation: Percentage/Ratio | 12 | 12 | 0 | Number | payments.csv | 1-2 step: filter + divide |
| 14 | Data Exploration | 12 | 12 | 0 | Mixed | payments.csv | 1 step: direct lookup/query |
| 15 | Counting: Transactions/Records | 11 | 11 | 0 | Number / String | payments.csv | 1 step: count/filter |
| 16 | Fee Comparison: MCC Fee Extremes | 10 | 0 | 10 | Number / list | fees.json + merchant_category_codes.csv | Multi-step: compute fees per MCC, rank |
| 17 | Fraud Analysis | 8 | 8 | 0 | Boolean / Number | payments.csv | 1-2 step: filter + compute rate |
| 18 | Fee Comparison: Cheapest Option | 8 | 0 | 8 | String | fees.json | Multi-step: compute + compare fees |
| 19 | Fee Comparison: Most Expensive Option | 8 | 0 | 8 | String | fees.json | Multi-step: compute + compare fees |
| 20 | Fee Impact: Merchants Affected | 7 | 0 | 7 | Comma-sep list | fees.json + payments.csv + merchant_data.json | Multi-step: match fee → merchants |
| 21 | Aggregation: Average | 5 | 5 | 0 | Number / String | payments.csv | 1-2 step: compute mean |
| 22 | Fee Analysis: Rate Factors | 5 | 5 | 0 | String / list | manual.md + fees.json | 1-2 step: read docs + reason |
| 23 | Counting: Unique Values | 4 | 4 | 0 | Number | payments.csv | 1 step: count distinct |
| 24 | Ranking: Bottom/Lowest | 1 | 1 | 0 | Number | payments.csv | 1-2 step: sort + pick |
| 25 | Fee: Other | 1 | 1 | 0 | String | manual.md | 1 step: doc lookup |
| | **TOTAL** | **450** | **72** | **378** | | | |

---

## Data Files Available to the Agent

All tasks share the same data directory (`/app/data/`) with 7 files downloaded from HuggingFace:

| File | Description | Role in Tasks |
|------|-------------|---------------|
| `payments.csv` | ~138,236 payment transactions with columns: psp_reference, merchant, card_scheme, aci, is_credit, eur_amount, ip_address, email_address, ip_country, issuing_country, shopper_interaction, has_fraudulent_dispute, etc. | Primary data source for 96% of tasks |
| `fees.json` | ~1,000 fee rules with fields: ID, card_scheme, account_type, aci, fixed_amount, rate, intracountry, merchant_category_code, is_credit, etc. | Required for 74% of tasks (all fee calculations) |
| `merchant_data.json` | Merchant profiles: name, merchant_category_code, account_type, capture_delay, monthly_volume, monthly_fraud_level | Required for fee matching (~40% of tasks) |
| `manual.md` | Documentation explaining fee structure, ACI types, rate factors, and payment processing concepts | Required for conceptual questions and fee reasoning |
| `merchant_category_codes.csv` | MCC code → description mapping | Required for MCC-related tasks (~7%) |
| `payments-readme.md` | Column descriptions for payments.csv | Helpful for understanding data schema |
| `acquirer_countries.csv` | Acquirer country codes | Required for country-related fee calculations |

---

## Answer Distribution

### By Answer Type

| Answer Type | Count | % | Difficulty Split |
|-------------|-------|---|------------------|
| **Number** (single numeric value) | 199 | 44.2% | 34 easy, 165 hard |
| **String** (word, name, letter) | 114 | 25.3% | 23 easy, 91 hard |
| **Comma-Separated List** (IDs, values) | 109 | 24.2% | 7 easy, 102 hard |
| **Grouped List** (key:value pairs) | 20 | 4.4% | 0 easy, 20 hard |
| **Boolean** (yes/no) | 6 | 1.3% | 6 easy, 0 hard |
| **Not Applicable** | 2 | 0.4% | 2 easy, 0 hard |

### Numeric Answer Statistics (199 tasks)

| Stat | Value |
|------|-------|
| Minimum | -10,499.55 |
| Maximum | 138,236 |
| Mean | 3,921.97 |
| Negative answers | Several (fee delta counterfactuals where fees decrease) |

### Answer Format Guidelines

| Format Specification | Count |
|----------------------|-------|
| Number rounded to 6 decimals | 92 |
| Comma-separated list | 109 |
| Number rounded to 2 decimals | 45 |
| Number rounded to 14 decimals | 40 |
| Card scheme + associated fee value | 30 |
| Single string value | 29 |
| ACI letter + associated fee value | 25 |
| Grouped list `[key: value, ...]` | 20 |
| Single letter (multiple choice) | 20 |
| Integer (no rounding) | 15 |
| Yes/No | 7 |
| Other formats | 18 |

### List Answer Complexity (109 comma-separated list tasks)

| Stat | Value |
|------|-------|
| Shortest list | 1 item |
| Longest list | 443 items |
| Average list length | 64 items |
| Empty lists (answer = "") | 3 tasks |

---

## Detailed Category Analysis

### Category 1: Fee Calculation — Average Fee by Card Scheme (60 tasks)

**All hard.** Compute the average fee a specific card scheme would charge for a given transaction value and card type.

**Pattern:** "For {credit/debit} transactions, what would be the average fee that {card_scheme} would charge for a transaction value of {X} EUR?"

**What it requires:**
1. Filter `fees.json` by card_scheme and is_credit
2. For each matching fee rule, compute: `fixed_amount + (rate × transaction_value)`
3. Average across all matching rules

**Example questions & answers:**
- Q: "For credit transactions, what would be the average fee that NexPay would charge for a transaction value of 10 EUR?" → **0.126459**
- Q: "For debit transactions, what would be the average fee that GlobalCard would charge for a transaction value of 500 EUR?" → **2.527255**

**Why it's hard for AI:** Requires understanding fee computation formula, correctly filtering a large JSON, and precise decimal arithmetic.

---

### Category 2: Fee Lookup — Applicable Fees for Merchant (45 tasks)

**All hard.** Find which fee IDs are applicable to a specific merchant on a specific day or in a specific month/year.

**Sub-patterns:**
- "For the {Nth} day of 2023, what are the Fee IDs applicable to {merchant}?" (30 tasks)
- "What were the applicable Fee IDs for {merchant} in {month} 2023?" (10 tasks)
- "What are the applicable fee IDs for {merchant} in 2023?" (5 tasks)

**What it requires:**
1. Look up merchant's profile in `merchant_data.json` (account_type, MCC, etc.)
2. Identify merchant's transactions on that day from `payments.csv`
3. For each transaction, match against all fee rules in `fees.json` checking: card_scheme, account_type, aci, MCC, is_credit, intracountry
4. Aggregate all matching fee IDs

**Example questions & answers:**
- Q: "For the 10th of the year 2023, what are the Fee IDs applicable to Belles_cookbook_store?" → **286, 381, 454, 473, 477, 536, 572, 709, 741, 813**
- Q: "What were the applicable Fee IDs for Crossfit_Hanna in March 2023?" → **29,36,51,64,65,89,107,...** (22+ IDs)

**Why it's hard for AI:** Multi-file cross-referencing with complex matching logic across many fields.

---

### Category 3: Fee Calculation — Total Fees for Merchant (45 tasks)

**All hard.** Compute the total fees (in EUR) a merchant should pay on a specific day of 2023.

**Pattern:** "For the {Nth} day of the year 2023, what is the total fees (in euros) that {merchant} should pay?"

**What it requires:**
1. Filter `payments.csv` for merchant + day
2. For each transaction, find applicable fee rules from `fees.json`
3. Compute fee per transaction: `fixed_amount + (rate × eur_amount)`
4. Sum all fees

**Example questions & answers:**
- Q: "...total fees that Belles_cookbook_store should pay [on day 10]?" → **29.93**
- Q: "...total fees that Crossfit_Hanna should pay [on day 200]?" → **99.32**

**Why it's hard for AI:** End-to-end fee pipeline — requires correct transaction-to-fee matching AND computation.

---

### Category 4: Counterfactual — Relative Fee Change (40 tasks)

**All hard.** Compute how much more/less a merchant would pay if a specific fee's relative rate changed.

**Pattern:** "In {month} 2023 what delta would {merchant} pay if the relative fee of the fee with ID={N} changed to {X}?"

**What it requires:**
1. Find all transactions matching fee ID={N} for that merchant/month
2. Compute original fees with current rate
3. Compute modified fees with new rate
4. Return the delta (difference)

**Example questions & answers:**
- Q: "In January 2023 what delta would Belles_cookbook_store pay if the relative fee of the fee with ID=398 changed to 1?" → **0**
- Q: "...if the relative fee of ID=64 changed to 99?" → **-10,499.55** (fees would decrease)

**Why it's hard for AI:** Multi-step counterfactual: understand fee structure, compute both scenarios, correctly calculate delta.

---

### Category 5: Fee Optimization — Steer Traffic to Card Scheme (30 tasks)

**All hard.** Determine which card scheme a merchant should route transactions through to minimize or maximize fees.

**Pattern:** "Looking at the month of {month}, to which card scheme should {merchant} steer traffic in order to pay the {minimum/maximum} fees?"

**What it requires:**
1. Get all transactions for merchant in that month
2. For each card scheme, compute total fees across all transactions
3. Return the card scheme with min or max total fees

**Example questions & answers:**
- Q: "...which card scheme should Belles_cookbook_store steer traffic to...minimum fees?" → **NexPay**
- Q: "...which card scheme should Crossfit_Hanna steer traffic to...maximum fees?" → **TransactPlus**

**Pattern observation:** NexPay is almost always cheapest; TransactPlus is almost always most expensive.

**Why it's hard for AI:** Full fee computation pipeline × 4 card schemes, then comparison.

---

### Category 6: Counterfactual — Preferred ACI (25 tasks)

**All hard.** Find the optimal ACI to redirect fraudulent transactions toward, to minimize fees.

**Pattern:** "For {merchant} in {month}, if we were to move the fraudulent transactions towards a different ACI by incentivizing users to use a different interaction, what would be the preferred choice considering the lowest possible fees?"

**What it requires:**
1. Identify fraudulent transactions for merchant in month
2. For each possible ACI, recompute fees for those transactions
3. Return the ACI that results in lowest total fees

**Example questions & answers:**
- Q: "For Golfclub_Baron_Friso in January..." → **E**
- Q: "For Crossfit_Hanna in February..." → **D**

**Why it's hard for AI:** Counterfactual fee recomputation across 7 ACI options for each fraudulent transaction.

---

### Category 7: Aggregation — Average by Group (20 tasks)

**All hard.** Compute average transaction value grouped by a specific dimension, for a specific merchant + card scheme + time period.

**Pattern:** "What is the average transaction value grouped by {dimension} for {merchant}'s {card_scheme} transactions between {month_start} and {month_end} 2023?"

**Dimensions used:** ip_country, issuing_country, card_scheme, shopper_interaction, aci

**Answer format:** `[key1:value1, key2:value2, ...]` sorted ascending by value

**Example questions & answers:**
- Q: "...grouped by ip_country for Belles_cookbook_store's SwiftCharge transactions between June and October 2023?" → **[GR:70.7, SE:83.8, LU:84.36, FR:88.59, IT:94.94, NL:108.81, BE:110.11, ES:126.92]**

**Why it's hard for AI:** Multi-filter + groupby + sort + specific output formatting.

---

### Category 8: Fee Comparison — Most Expensive ACI (20 tasks)

**All hard.** Find which ACI produces the highest fee for a given transaction amount, card type, and card scheme.

**Pattern:** "For a {credit/debit} transaction of {X} euros on {card_scheme}, what would be the most expensive ACI?"

**Example questions & answers:**
- Q: "For a credit transaction of 1 euros on GlobalCard..." → **C**
- Q: "For a debit transaction of 500 euros on NexPay..." → **F**

---

### Category 9: Fee Lookup — Fee IDs by Conditions (20 tasks)

**All hard.** Find all fee IDs matching a combination of account_type and aci.

**Pattern:** "What is the fee ID or IDs that apply to account_type = {X} and aci = {Y}?"

**Example questions & answers:**
- Q: "...account_type = R and aci = A?" → **3,4,5,7,8,9,11,15,...** (50+ IDs)
- Q: "...account_type = O and aci = C?" → **1,3,4,5,8,9,11,...** (370+ IDs)

**Answers can be very long** (up to 443 comma-separated fee IDs).

---

### Category 10: Counterfactual — MCC Code Change (20 tasks)

**All hard.** Compute fee delta if a merchant changed its MCC code.

**Pattern:** "Imagine the merchant {merchant} had changed its MCC code to {XXXX} before 2023 started, what amount delta will it have to pay in fees for the year 2023?"

**Example questions & answers:**
- Q: "...Belles_cookbook_store changed MCC to 8062..." → **5841.0**
- Q: "...Crossfit_Hanna changed MCC to 5411..." → **18657.348907**

---

### Category 11: Counterfactual — Fee Scenario (20 tasks)

**All hard.** What-if scenarios involving fee rule modifications applied to specific merchants.

**Pattern:** "During 2023, imagine if the Fee with ID {N} was only applied to account type {X}, which merchants would be affected?" or "what would be the delta?"

**Example questions & answers:**
- Q: "...if Fee ID 17 was only applied to account type D, which merchants would be affected?" → **(empty — no merchants)**
- Q: "...if Fee ID 65 had a fixed fee of 2, what would be the total delta?" → **14.95**

---

### Categories 12-25: Easy Tasks (72 tasks total)

All 72 easy tasks are basic data exploration on `payments.csv` (and occasionally `manual.md`). They break down as:

| Sub-category | Count | Example Question | Example Answer |
|-------------|-------|------------------|----------------|
| **Ranking: Top/Highest** | 13 | "Which card scheme is the most commonly used?" | GlobalCard |
| **Aggregation: Percentage/Ratio** | 12 | "What percentage of transactions are made using credit cards?" | 73.15 |
| **Data Exploration** | 12 | "What is the name of the column that indicates fraud?" | has_fraudulent_dispute |
| **Counting: Transactions** | 11 | "How many total transactions are there in the dataset?" | 138236 |
| **Fraud Analysis** | 8 | "Is the fraud rate for ecommerce transactions higher than in-store?" | yes |
| **Aggregation: Average** | 5 | "What is the average transaction amount (in EUR)?" | 91.85 |
| **Fee Analysis: Rate Factors** | 5 | "Which factors contribute to a cheaper fee rate if increased?" | monthly_volume,capture_delay |
| **Counting: Unique Values** | 4 | "How many unique merchants are present in the dataset?" | 5 |
| **Ranking: Bottom/Lowest** | 1 | "What is the lowest avg fraud rate per merchant for 2023?" | 8.91 |
| **Fee: Other** | 1 | "How much is the excessive retry fee?" | Not Applicable |

**Why easy tasks are easy:** Single data file, 1-2 step computation, no cross-referencing required.

---

## Task Templating Patterns

Many categories are parametric variations of the same template. This is important for evaluation because:
- **High correlation within categories:** If an agent solves one, it likely solves all variants
- **Systematic errors compound:** A wrong fee-matching algorithm fails across entire categories

| Category | Template Parameters | Variations |
|----------|-------------------|------------|
| Avg Fee by Card Scheme | card_scheme (4) × transaction_value (8) × is_credit (2) | = 60 |
| Total Fees for Merchant | merchant (5) × day_of_year (varies) | = 45 |
| Applicable Fees for Merchant | merchant (5) × time_period (varies) | = 45 |
| Relative Fee Change | merchant (5) × fee_id × month × new_rate | = 40 |
| Steer Traffic | merchant (5) × month (12) × min/max (2) | = 30 |
| Preferred ACI | merchant (5) × month (12) | = 25 |
| Average by Group | merchant × card_scheme × dimension × time | = 20 |
| Most Expensive ACI | card_scheme (4) × amount (5) × is_credit (2) | = 20 |
| Fee IDs by Conditions | account_type (6) × aci (varies) | = 20 |
| MCC Code Change | merchant (5) × new_MCC (4) | = 20 |

---

## Data Sources Required by Task Count

| Data Source Combination | Task Count | % |
|------------------------|------------|---|
| fees.json only | 118 | 26.2% |
| fees.json + payments.csv | 142 | 31.6% |
| payments.csv only | 58 | 12.9% |
| fees.json + payments.csv + merchant_data.json + MCC codes | 40 | 8.9% |
| fees.json + manual.md + payments.csv | 23 | 5.1% |
| fees.json + manual.md | 22 | 4.9% |
| manual.md + payments.csv | 20 | 4.4% |
| Other combinations | 27 | 6.0% |

**Key insight:** 273 tasks (61%) require cross-referencing 2+ data files. All hard tasks require at least 2 files.

---

## Keyword Frequency in Questions

| Keyword | Appearances | Notes |
|---------|-------------|-------|
| fee | 334 | 74% of all tasks involve fees |
| transaction | 190 | Most tasks reference transaction data |
| average | 101 | Averaging is the most common operation |
| merchant | 94 | Merchant-specific questions common |
| if the / change | 92 / 80 | Counterfactual reasoning |
| aci | 71 | Authorization Characteristics Indicator |
| total | 48 | Sum/total computations |
| lowest | 47 | Finding minimums |
| delta | 60 | Fee change impact |
| fraudulent | 33 | Fraud-related filtering |
| grouped by | 20 | Aggregation by dimension |
| SwiftCharge / NexPay / GlobalCard / TransactPlus | 30 / 24 / 24 / 24 | The 4 card schemes |
| account_type | 21 | Fee filtering dimension |
| percentage | 11 | Ratio computations |
| unique | 7 | Distinct counting |

---

## Difficulty Analysis

### What Makes a Task "Easy" (72 tasks)
- **Single data source:** Almost all use only `payments.csv`
- **1-2 reasoning steps:** Count, filter, average, or look up a value
- **No fee calculation:** No need to understand `fees.json` structure
- **Standard pandas operations:** `df.groupby()`, `df.mean()`, `df.value_counts()`, `df.nunique()`

### What Makes a Task "Hard" (378 tasks)
- **Multiple data sources:** Cross-reference 2-4 files
- **Fee computation logic:** Must understand `fee = fixed_amount + (rate × transaction_amount)`
- **Complex matching:** Fee rules have nullable fields (None means "applies to all"), requiring careful filter logic
- **Counterfactual reasoning:** Modify parameters and recompute
- **Large output space:** Some answers are lists of 100+ fee IDs
- **Precise decimal requirements:** Many answers require 6 or 14 decimal places

### Difficulty by Answer Complexity

| Metric | Easy Tasks | Hard Tasks |
|--------|-----------|------------|
| Avg answer length (chars) | 14 | 78 |
| Max answer length | 131 | 1,723 |
| Tasks with list answers | 7 (10%) | 122 (32%) |
| Tasks requiring 3+ files | 0 | 87 (23%) |

---

## Observations for AI Agent Evaluation

### 1. Fee Matching is the Core Challenge
The fundamental skill being tested is: **given a transaction and a set of fee rules, determine which rules apply and compute the fee.** This requires:
- Handling nullable fields in fee rules (None = wildcard)
- Matching on multiple dimensions simultaneously (card_scheme, account_type, aci, MCC, is_credit, intracountry)
- Correct arithmetic with fixed_amount + rate × amount

### 2. High Leverage from Getting Fee Matching Right
If an agent correctly implements the fee-matching algorithm, it can potentially solve ~74% of all tasks (334 out of 450). The templated nature means one correct implementation unlocks entire categories.

### 3. Easy Tasks are a Good Warmup / Sanity Check
The 72 easy tasks test basic data literacy. An agent that can't answer "How many transactions are there?" has no hope with fee calculations.

### 4. Answer Format Precision Matters
Many tasks require specific decimal precision (6 or 14 places), sorted lists, or specific formatting (`[key: value, ...]`). Format errors could cause failures even when the computation is correct.

### 5. "Not Applicable" is Rare but Tricky
Only 2 tasks have "Not Applicable" as the answer. An agent needs to recognize when a question can't be answered from the available data.

### 6. Empty Answers Exist
3 tasks have empty string answers (no merchants affected by a fee). The agent must handle the edge case of an empty result set.

### 7. Recommended Evaluation Strategy
- **Tier 1 (sanity check):** Run the 72 easy tasks first (~16% of benchmark)
- **Tier 2 (core capability):** Run 1-2 tasks per hard category to test fee-matching ability (~25 tasks)
- **Tier 3 (full benchmark):** Run all 450 for comprehensive scoring
- **Category-level scoring** is more informative than overall accuracy due to templating

---

## Appendix: All 5 Merchants in Dataset

| Merchant | Appears in Questions | Notes |
|----------|---------------------|-------|
| Belles_cookbook_store | ~100 tasks | Used across all fee categories |
| Crossfit_Hanna | ~100 tasks | Highest transaction volume |
| Golfclub_Baron_Friso | ~80 tasks | |
| Martinis_Fine_Steakhouse | ~80 tasks | |
| Rafa_AI | ~60 tasks | |

## Appendix: All 4 Card Schemes

| Card Scheme | Used In | Typical Fee Level |
|-------------|---------|-------------------|
| GlobalCard | 24+ tasks | Usually cheapest |
| NexPay | 24+ tasks | Often cheapest for steering |
| SwiftCharge | 30+ tasks | Mid-range |
| TransactPlus | 24+ tasks | Usually most expensive |

## Appendix: ACI Values

The 7 Authorization Characteristics Indicator values: **A, B, C, D, E, F, G**

These represent different transaction authentication methods (e.g., Ecommerce, POS, MOTO) and significantly impact fee rates.
