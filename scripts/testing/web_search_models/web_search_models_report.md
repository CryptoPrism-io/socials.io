# Web Search Models Bitcoin Test Report

**Generated:** 2025-09-23 14:00:03
**Test Prompt:** Bitcoin current information with JSON response
**Total Models Tested:** 11
**Successful:** 10
**Failed:** 1

## Executive Summary

This report evaluates web search-enabled language models for real-time Bitcoin information retrieval. Models were tested for accuracy, response time, token efficiency, and cost-effectiveness.

## Model Performance Overview

| Model | Success | Response Time | Tokens | Cost (USD) | JSON Valid |
|-------|---------|---------------|--------|------------|-------------|
| Perplexity Sonar Pro | ✅ | 6.29s | 320 | $0.002880 | ✅ |
| Perplexity Reasoning Pro | ✅ | 9.50s | 566 | $0.006498 | ❌ |
| Perplexity Deep Research | ✅ | 26.99s | 442 | $0.007730 | ❌ |
| Perplexity Reasoning | ✅ | 8.90s | 566 | $0.004332 | ❌ |
| Perplexity Sonar | ✅ | 5.49s | 308 | $0.001800 | ✅ |
| Perplexity R1-1776 | ❌ | 0.89s | 0 | $0.000000 | ❌ |
| GPT-4o Search Preview | ✅ | 7.87s | 366 | $0.007780 | ✅ |
| GPT-4o Mini Search | ✅ | 4.09s | 324 | $0.001224 | ✅ |
| Alibaba Deep Research | ✅ | 5.74s | 498 | $0.003588 | ✅ |
| Hermes 4 70B | ✅ | 2.44s | 315 | $0.001678 | ✅ |
| Hermes 4 405B | ✅ | 3.51s | 291 | $0.001438 | ✅ |


## Detailed Results


### 1. Perplexity Sonar Pro

**Model ID:** `perplexity/sonar-pro`
**Status:** ✅ Success
**Response Time:** 6.29 seconds
**Timestamp:** 2025-09-23 13:58:36

**Token Usage:**
- Prompt Tokens: 160
- Completion Tokens: 160
- Total Tokens: 320
- Estimated Cost: $0.002880

**Content Length:** 529 characters
**JSON Parsed:** ✅ Yes

**Parsed Bitcoin Data:**
```json
{
  "current_price": "$118,838",
  "past_24h": [
    "BTC dipped below $113,000 before rebounding",
    "Over $285M in leveraged long liquidations occurred",
    "BTC up more than 3% from September lows"
  ],
  "next_24h": [
    "Watch for BTC to hold above $110,000 support",
    "Potential test of $117,500-$118,000 resistance",
    "Monitor capital inflows to spot and perpetual exchanges"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "$107,500",
    "resistance": "$117,500-$118,000"
  }
}
```

**Key Information Extracted:**
- 💰 **Current Price:** $118,838
- 📊 **Market Sentiment:** bullish
- 🎯 **Support Level:** $107,500
- 🎯 **Resistance Level:** $117,500-$118,000

**Past 24H Events:**
- BTC dipped below $113,000 before rebounding
- Over $285M in leveraged long liquidations occurred
- BTC up more than 3% from September lows

**Next 24H Outlook:**
- Watch for BTC to hold above $110,000 support
- Potential test of $117,500-$118,000 resistance
- Monitor capital inflows to spot and perpetual exchanges

**Raw Response:**
```
```json
{
  "current_price": "$118,838",
  "past_24h": [    "BTC dipped below $113,000 before rebounding",
    "Over $285M in leveraged long liquidations occurred",
    "BTC up more than 3% from September lows"
  ],
  "next_24h": [    "Watch for BTC to hold above $110,000 support",
    "Potential test of $117,500-$118,000 resistance",
    "Monitor capital inflows to spot and perpetual exchanges"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "$107,500",
    "resistance": ...
```

---

### 2. Perplexity Reasoning Pro

**Model ID:** `perplexity/sonar-reasoning-pro`
**Status:** ✅ Success
**Response Time:** 9.50 seconds
**Timestamp:** 2025-09-23 13:58:47

**Token Usage:**
- Prompt Tokens: 166
- Completion Tokens: 400
- Total Tokens: 566
- Estimated Cost: $0.006498

**Content Length:** 303 characters
**JSON Parsed:** ❌ No


**Raw Response:**
```
```json
{
  "current_price": "$118,838.03",
  "past_24h": [
    "BTC declined over 3% in past two days below $113,000",
    "$285M leveraged long liquidations triggered on Sep 22",
    "Price dropped 0.50% today losing $602.06"
  ],
  "next_24h": [
    "Watch if BTC holds support above $110,000",
    "
```

---

### 3. Perplexity Deep Research

**Model ID:** `perplexity/sonar-deep-research`
**Status:** ✅ Success
**Response Time:** 26.99 seconds
**Timestamp:** 2025-09-23 13:59:15

**Token Usage:**
- Prompt Tokens: 166
- Completion Tokens: 276
- Total Tokens: 442
- Estimated Cost: $0.007730

**Content Length:** 0 characters
**JSON Parsed:** ❌ No


**Raw Response:**
```

```

---

### 4. Perplexity Reasoning

**Model ID:** `perplexity/sonar-reasoning`
**Status:** ✅ Success
**Response Time:** 8.90 seconds
**Timestamp:** 2025-09-23 13:59:25

**Token Usage:**
- Prompt Tokens: 166
- Completion Tokens: 400
- Total Tokens: 566
- Estimated Cost: $0.004332

**Content Length:** 0 characters
**JSON Parsed:** ❌ No


**Raw Response:**
```

```

---

### 5. Perplexity Sonar

**Model ID:** `perplexity/sonar`
**Status:** ✅ Success
**Response Time:** 5.49 seconds
**Timestamp:** 2025-09-23 13:59:31

**Token Usage:**
- Prompt Tokens: 160
- Completion Tokens: 148
- Total Tokens: 308
- Estimated Cost: $0.001800

**Content Length:** 451 characters
**JSON Parsed:** ✅ Yes

**Parsed Bitcoin Data:**
```json
{
  "current_price": "118,838.03 USD",
  "past_24h": [
    "BTC dipped below $113,000 on Sept 22",
    "Bitcoin price down -0.50% today",
    "Long/short ratio bullish above 1"
  ],
  "next_24h": [
    "Watch if BTC recovers above $118,000",
    "Monitor fresh capital inflows",
    "Observe if September ends in red"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "113,000 USD",
    "resistance": "118,000 USD"
  }
}
```

**Key Information Extracted:**
- 💰 **Current Price:** 118,838.03 USD
- 📊 **Market Sentiment:** bullish
- 🎯 **Support Level:** 113,000 USD
- 🎯 **Resistance Level:** 118,000 USD

**Past 24H Events:**
- BTC dipped below $113,000 on Sept 22
- Bitcoin price down -0.50% today
- Long/short ratio bullish above 1

**Next 24H Outlook:**
- Watch if BTC recovers above $118,000
- Monitor fresh capital inflows
- Observe if September ends in red

**Raw Response:**
```
```json
{
  "current_price": "118,838.03 USD",
  "past_24h": [    "BTC dipped below $113,000 on Sept 22",
    "Bitcoin price down -0.50% today",
    "Long/short ratio bullish above 1"
  ],
  "next_24h": [    "Watch if BTC recovers above $118,000",
    "Monitor fresh capital inflows",
    "Observe if September ends in red"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "113,000 USD",
    "resistance": "118,000 USD"
  }
}
```
```

---

### 6. Perplexity R1-1776

**Model ID:** `perplexity/r1-1776`
**Status:** ❌ Failed
**Response Time:** 0.89 seconds
**Timestamp:** 2025-09-23 13:59:33

**Error:** Provider returned error

---

### 7. GPT-4o Search Preview

**Model ID:** `openai/gpt-4o-search-preview`
**Status:** ✅ Success
**Response Time:** 7.87 seconds
**Timestamp:** 2025-09-23 13:59:42

**Token Usage:**
- Prompt Tokens: 160
- Completion Tokens: 206
- Total Tokens: 366
- Estimated Cost: $0.007780

**Content Length:** 688 characters
**JSON Parsed:** ✅ Yes

**Parsed Bitcoin Data:**
```json
{
  "current_price": "$113,216",
  "past_24h": [
    "Bitcoin hits $100,000 milestone",
    "FBI seizes $2.4M in Bitcoin",
    "Czech bank plans Bitcoin reserves"
  ],
  "next_24h": [
    "Congress reviews crypto bills",
    "Market reacts to Fed decisions",
    "Bitcoin ETF inflows continue"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "$110,000",
    "resistance": "$118,000"
  }
}
```

**Key Information Extracted:**
- 💰 **Current Price:** $113,216
- 📊 **Market Sentiment:** bullish
- 🎯 **Support Level:** $110,000
- 🎯 **Resistance Level:** $118,000

**Past 24H Events:**
- Bitcoin hits $100,000 milestone
- FBI seizes $2.4M in Bitcoin
- Czech bank plans Bitcoin reserves

**Next 24H Outlook:**
- Congress reviews crypto bills
- Market reacts to Fed decisions
- Bitcoin ETF inflows continue

**Raw Response:**
```
```json
{
  "current_price": "$113,216",
  "past_24h": [
    "Bitcoin hits $100,000 milestone",
    "FBI seizes $2.4M in Bitcoin",
    "Czech bank plans Bitcoin reserves"
  ],
  "next_24h": [
    "Congress reviews crypto bills",
    "Market reacts to Fed decisions",
    "Bitcoin ETF inflows continue"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "$110,000",
    "resistance": "$118,000"
  }
}
```
## Stock market information for Bitcoin (BTC)
- Bitcoin is a crypto in the C...
```

---

### 8. GPT-4o Mini Search

**Model ID:** `openai/gpt-4o-mini-search-preview`
**Status:** ✅ Success
**Response Time:** 4.09 seconds
**Timestamp:** 2025-09-23 13:59:47

**Token Usage:**
- Prompt Tokens: 160
- Completion Tokens: 164
- Total Tokens: 324
- Estimated Cost: $0.001224

**Content Length:** 558 characters
**JSON Parsed:** ✅ Yes

**Parsed Bitcoin Data:**
```json
{
  "current_price": "113,216.0 USD",
  "past_24h": [
    "Bitcoin price increased by $532.00 (0.47%)",
    "Intraday high reached $113,469.0 USD",
    "Intraday low was $111,644.0 USD"
  ],
  "next_24h": [
    "Monitor potential market reactions to upcoming U.S. crypto legislation",
    "Watch for Bitcoin's response to global economic indicators",
    "Observe institutional investment trends in the crypto market"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "111,644.0 USD",
    "resistance": "113,469.0 USD"
  }
}
```

**Key Information Extracted:**
- 💰 **Current Price:** 113,216.0 USD
- 📊 **Market Sentiment:** bullish
- 🎯 **Support Level:** 111,644.0 USD
- 🎯 **Resistance Level:** 113,469.0 USD

**Past 24H Events:**
- Bitcoin price increased by $532.00 (0.47%)
- Intraday high reached $113,469.0 USD
- Intraday low was $111,644.0 USD

**Next 24H Outlook:**
- Monitor potential market reactions to upcoming U.S. crypto legislation
- Watch for Bitcoin's response to global economic indicators
- Observe institutional investment trends in the crypto market

**Raw Response:**
```
```json
{
  "current_price": "113,216.0 USD",
  "past_24h": [
    "Bitcoin price increased by $532.00 (0.47%)",
    "Intraday high reached $113,469.0 USD",
    "Intraday low was $111,644.0 USD"
  ],
  "next_24h": [
    "Monitor potential market reactions to upcoming U.S. crypto legislation",
    "Watch for Bitcoin's response to global economic indicators",
    "Observe institutional investment trends in the crypto market"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "11...
```

---

### 9. Alibaba Deep Research

**Model ID:** `alibaba/tongyi-deepresearch-30b-a3b`
**Status:** ✅ Success
**Response Time:** 5.74 seconds
**Timestamp:** 2025-09-23 13:59:54

**Token Usage:**
- Prompt Tokens: 174
- Completion Tokens: 324
- Total Tokens: 498
- Estimated Cost: $0.003588

**Content Length:** 525 characters
**JSON Parsed:** ✅ Yes

**Parsed Bitcoin Data:**
```json
{
  "current_price": "$69,850.12",
  "past_24h": [
    "Fed's Powell hints at cautious rate cuts amid sticky inflation",
    "El Salvador buys $5M Bitcoin adding to reserves",
    "Coinbase launches USDC staking with 5% APY"
  ],
  "next_24h": [
    "US CPI data release (June) - inflation expectations",
    "Bitcoin ETF net flows monitoring",
    "Ethereum Shanghai upgrade aftermath analysis"
  ],
  "market_sentiment": "Bullish",
  "key_levels": {
    "support": "$68,500",
    "resistance": "$71,000"
  }
}
```

**Key Information Extracted:**
- 💰 **Current Price:** $69,850.12
- 📊 **Market Sentiment:** Bullish
- 🎯 **Support Level:** $68,500
- 🎯 **Resistance Level:** $71,000

**Past 24H Events:**
- Fed's Powell hints at cautious rate cuts amid sticky inflation
- El Salvador buys $5M Bitcoin adding to reserves
- Coinbase launches USDC staking with 5% APY

**Next 24H Outlook:**
- US CPI data release (June) - inflation expectations
- Bitcoin ETF net flows monitoring
- Ethereum Shanghai upgrade aftermath analysis

**Raw Response:**
```


```json
{
  "current_price": "$69,850.12",
  "past_24h": [
    "Fed's Powell hints at cautious rate cuts amid sticky inflation",
    "El Salvador buys $5M Bitcoin adding to reserves",
    "Coinbase launches USDC staking with 5% APY"
  ],
  "next_24h": [
    "US CPI data release (June) - inflation expectations",
    "Bitcoin ETF net flows monitoring",
    "Ethereum Shanghai upgrade aftermath analysis"
  ],
  "market_sentiment": "Bullish",
  "key_levels": {
    "support": "$68,500",
    "resista...
```

---

### 10. Hermes 4 70B

**Model ID:** `nousresearch/hermes-4-70b`
**Status:** ✅ Success
**Response Time:** 2.44 seconds
**Timestamp:** 2025-09-23 13:59:57

**Token Usage:**
- Prompt Tokens: 184
- Completion Tokens: 131
- Total Tokens: 315
- Estimated Cost: $0.001678

**Content Length:** 443 characters
**JSON Parsed:** ✅ Yes

**Parsed Bitcoin Data:**
```json
{
  "current_price": "$27,300.50",
  "past_24h": [
    "BTC breaks above $27,000 resistance level",
    "Fed keeps interest rates unchanged",
    "Whales accumulate BTC, on-chain data shows"
  ],
  "next_24h": [
    "Monitor $27,500 resistance level",
    "Watch for CPI data release impact",
    "Analyze BTC dominance trends"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "$26,800",
    "resistance": "$27,500"
  }
}
```

**Key Information Extracted:**
- 💰 **Current Price:** $27,300.50
- 📊 **Market Sentiment:** bullish
- 🎯 **Support Level:** $26,800
- 🎯 **Resistance Level:** $27,500

**Past 24H Events:**
- BTC breaks above $27,000 resistance level
- Fed keeps interest rates unchanged
- Whales accumulate BTC, on-chain data shows

**Next 24H Outlook:**
- Monitor $27,500 resistance level
- Watch for CPI data release impact
- Analyze BTC dominance trends

**Raw Response:**
```
{
  "current_price": "$27,300.50",
  "past_24h": [
    "BTC breaks above $27,000 resistance level",
    "Fed keeps interest rates unchanged",
    "Whales accumulate BTC, on-chain data shows"
  ],
  "next_24h": [
    "Monitor $27,500 resistance level",
    "Watch for CPI data release impact",
    "Analyze BTC dominance trends"
  ],
  "market_sentiment": "bullish",
  "key_levels": {
    "support": "$26,800",
    "resistance": "$27,500"
  }
}
```

---

### 11. Hermes 4 405B

**Model ID:** `nousresearch/hermes-4-405b`
**Status:** ✅ Success
**Response Time:** 3.51 seconds
**Timestamp:** 2025-09-23 14:00:02

**Token Usage:**
- Prompt Tokens: 184
- Completion Tokens: 107
- Total Tokens: 291
- Estimated Cost: $0.001438

**Content Length:** 355 characters
**JSON Parsed:** ✅ Yes

**Parsed Bitcoin Data:**
```json
{
  "current_price": "Bitcoin price is $27,300",
  "past_24h": [
    "Bitcoin dipped below $27,000",
    "Regained $27,000 level",
    "Trading volume increased"
  ],
  "next_24h": [
    "Fed meeting minutes",
    "Inflation data release",
    "Technical levels to watch"
  ],
  "market_sentiment": "Neutral",
  "key_levels": {
    "support": "$26,500",
    "resistance": "$28,000"
  }
}
```

**Key Information Extracted:**
- 💰 **Current Price:** Bitcoin price is $27,300
- 📊 **Market Sentiment:** Neutral
- 🎯 **Support Level:** $26,500
- 🎯 **Resistance Level:** $28,000

**Past 24H Events:**
- Bitcoin dipped below $27,000
- Regained $27,000 level
- Trading volume increased

**Next 24H Outlook:**
- Fed meeting minutes
- Inflation data release
- Technical levels to watch

**Raw Response:**
```
{
  "current_price": "Bitcoin price is $27,300",
  "past_24h": ["Bitcoin dipped below $27,000", "Regained $27,000 level", "Trading volume increased"],
  "next_24h": ["Fed meeting minutes", "Inflation data release", "Technical levels to watch"],
  "market_sentiment": "Neutral",
  "key_levels": {
    "support": "$26,500",
    "resistance": "$28,000"
  }
}
```

---

## Cost Analysis

| Metric | Value |
|--------|-------|
| Total Cost (All Successful) | $0.038948 |
| Average Cost per Request | $0.003895 |
| Lowest Cost Model | $0.001224 |
| Highest Cost Model | $0.007780 |

## Recommendations

**Best Overall Performance:**

- **Most Cost-Effective:** GPT-4o Mini Search ($0.001224)
- **Fastest Response:** Hermes 4 70B (2.44s)

**For Production Use:**
1. **Primary:** Models with JSON parsing success and reasonable cost
2. **Fallback:** Standard models without web search for reliability


## Technical Notes

- All tests used the same prompt asking for current Bitcoin information in JSON format
- Response times include network latency
- Costs are estimated based on published pricing (may vary)
- JSON parsing indicates structured data extraction capability
- Models are ranked by success rate, then by cost-effectiveness

**Test Configuration:**
- Max Tokens: 400
- Temperature: 0.2
- Timeout: 30 seconds
- Prompt Length: ~93 characters

---
*Report generated by socials.io automated testing system*
