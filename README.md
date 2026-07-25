# ⚽ Football Match Outcome Prediction System

A machine learning pipeline for predicting football match outcomes and evaluating betting strategies using historical match data and bookmaker odds.

## 📊 Project Overview

This project implements an end-to-end **ELT (Extract–Load–Transform)** pipeline and ML workflow using approximately **14,000 matches** from **12 European leagues** across **4 seasons (2020–2024)**.

Main components:

- Web scraping and data validation
- Feature engineering from match statistics
- Decision Tree and Random Forest classifiers
- Confidence-based betting strategy
- Historical bankroll simulations using the Kelly Criterion

## 📁 Project Structure

```text
src/            Scrapers and data processing
data/           Raw, transformed and processed datasets
notebooks/      EDA, modelling and validation
models/         Trained models
charts/         Visualisations
```

## 🔬 Methodology

1. Collect match statistics and betting odds.
2. Transform raw data into ML-ready features.
3. Train classification models.
4. Place bets only when predicted probability provides positive expected value.
5. Evaluate both predictive performance and betting profitability.

## 📈 Results

Cross-validation showed that confidence thresholding improves both accuracy and profitability compared to betting every match.

### Betting simulation

- EV threshold: **1.2**
- Bets placed: **461 / 3564 matches (13%)**
- Best strategy:
  - Kelly fraction **0.2**
  - **2 selections** per betting ticket
  - **Median ROI: 222.58%**
  - **89%** of simulations finished with profit

The simulations demonstrate the trade-off between return and risk. Single-bet strategies produced lower median ROI (~90–110%) but substantially reduced downside risk.

I encourage to test other results and configuration - run the chapter 6 and play with configuration

## ⚠️ Current Limitations

- Only four historical seasons were available.
- Odds correspond to values available immediately before kick-off.
- The Flashscore scraper currently requires updates because the website structure has changed.

## 🚀 Future Work

Below there is a proposal for extending the project:

- Extend the dataset with 2–3 additional seasons.
- Rolling time-window validation (3 train + 1 test).
- Time-series form features.
- Benchmark XGBoost and LightGBM.
- Hyperparameter optimisation.
- Support bookmaker-specific odds.

## 🛠 Requirements

- Python **3.10+**

Install all dependencies with (I hope I did not miss anything):

```bash
pip install -r requirements.txt
```

## 🎓 Academic Context

Developed as part of a Master's thesis on machine learning for football prediction and betting market efficiency.

## ⚠ Disclaimer

Educational and research purposes only. Sports betting involves financial risk and past performance does not guarantee future results.
