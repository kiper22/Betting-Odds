# TODO
Make professional readme, not a draft like now (because this part is being submitted as a project for a class/course)
Feature Engineering:
- Add average statistics from the previous 1, 3, and 5 matches to enrich the dataset with recent form indicators.

Data Selection:
- Improve data filtering and selection to ensure the quality and relevance of input features for the model.

Model Approach Update:
- Change the current model evaluation method from accuracy-based to a more realistic scenario.
- Instead of static train-test splits, implement a framework where the model trains on historical data and predicts future matches sequentially.
- This would allow incremental training as new data becomes available and more accurate forecasting.

Expand Time Series Models:
- Develop the existing time series model prototypes further.
- Implement advanced models such as LSTM (Long Short-Term Memory networks) to better capture temporal dependencies and improve predictions.

Betting Strategy Finalization:
- Add a comprehensive chapter on finalizing the betting system — from selecting the best matches to place bets on, to evaluating the profitability and risk of the betting slips.
- This should include methodology, metrics, and practical considerations for real-world application.

# Project Overview

The project begins with the sequential execution of scripts designed to collect and extract football match data from specified web sources:

    src/extract_pages.py — This script downloads the raw HTML pages for the leagues listed in src/links.json. The pages are saved in the data/raw_html directory.

    src/extract_ids.py — This script parses the previously saved HTML pages to extract internal match IDs used by the data source. The extracted IDs are stored in the data/match_ids folder.

    src/fill_data.py — Using the saved match IDs, this script collects detailed match data and saves it as CSV files in data/extracted_data. If any errors occur during the process, they are logged into .log files for review.

    log_exception_handler.py — A utility for interactively removing erroneous rows from datasets based on full log traceback entries. Useful for reviewing issues caused by site structure changes or failed fetch attempts.

    ids_csv_list_exception_handler.py — A simpler version that removes rows based on a plain list of problematic match IDs (e.g., compiled manually or extracted from logs).

    src/analysis.ipynb — The main Jupyter notebook containing the complete data analysis process, integrity checks, exploratory visualizations, and model-related experiments.

# Notes and Considerations

Throughout the development of this project (spanning several months), minor structural changes were introduced to the source website. This occasionally required adjustments to the scraping logic—particularly the part responsible for generating the CSV files with extracted match data.

During final analysis, it was discovered that some columns related to handicap betting markets contained partially incorrect data. While the bulk of the information appeared intact, certain edge cases went unnoticed earlier due to silent failures in parsing or incomplete fetches.

It was often necessary to re-run scripts for specific matches when data was not retrieved successfully on the first attempt. Increasing wait times between requests typically solved these issues.

The manual row-removal tools were used to clean up problematic data:

    leagues with ambiguous structures (e.g., relegation groups, playoffs, or regional cups),

    single matches that defied standard assumptions,

    or formats involving group stages followed by knockout rounds (which require distinct handling in modeling workflows due to their different logic and data context).
