# Introduction

The project focuses on developing a model for sports betting decision-making. It begins with data acquisition (web scraping), followed by data processing and preparation for model building. A Decision Tree (DT) model was selected due to its explainability and the ability to clearly understand the decision-making process.

At the current stage, the project is nearing completion. The remaining work includes improving feature selection for the Decision Tree, refining the model itself, and evaluating its performance in a realistic setting. This involves running several hundred trials on an unseen dataset, while also accounting for practical factors such as the number of bets per ticket and applicable taxes.

Finally, once all of the above steps are completed, a thorough review will be required to further refine and polish the project, ensuring it is presented in the clearest and most understandable form possible.

PS. Latest part of the project is partially written in polish - will be fixed

**Main file (analysys) is in SRC folder**


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
