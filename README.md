LLMTCPH-Standalone
Overview

LLMTCPH-Standalone is a project that focuses on analyzing and benchmarking SQL query complexity using various AI models. The project includes scripts for evaluating SQL queries, generating complexity scores, and visualizing the results.
Repository Structure

    benchmark_queries/: Contains SQL query samples used for benchmarking.
    expected_results/: Stores the expected outcomes for the benchmark queries.
    prompts/: Includes prompt templates for AI models.
    .gitignore: Specifies files and directories to be ignored by Git.
    LICENSE: Contains the licensing information for the project.
    Project Data Analysis.pbix: A Power BI file for data analysis and visualization.
    SQL Query Complexity Score.py: A Python script for calculating SQL query complexity scores.
    ai.py: Script related to AI model interactions.
    helpers.py: Contains helper functions used across the project.
    main.py: The main script to execute the project.
    models.json: Configuration file listing the models used.
    results.db: Database file storing the results of the analyses.
    test.py: Script for testing the functionalities.
    tpch_questions.json: JSON file containing TPC-H benchmark questions.

Getting Started
Prerequisites

    Python 3.x
    Required Python libraries (listed in requirements.txt)

Installation

    Clone the repository:
    git clone https://github.com/ArafatAhmed00/LLMTCPH-Standalone.git
    Navigate to the project directory:
    cd LLMTCPH-Standalone
    Install the required dependencies:
    pip install -r requirements.txt

Usage

    Prepare your SQL queries: Place your SQL queries in the benchmark_queries/ directory.
    Run the main script:
    python main.py
    Analyze the results: Use the Project Data Analysis.pbix file with Power BI to visualize and interpret the complexity scores.

License

This project is licensed under the BSD-3-Clause License. See the LICENSE file for more details.
Acknowledgments

Special thanks to the contributors and the open-source community for their invaluable support and resources.

