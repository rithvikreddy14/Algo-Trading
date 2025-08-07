Algo-Trading Prototype with ML & Automation
===========================================

This is a Python-based mini algo-trading prototype designed to demonstrate a basic automated trading workflow. The system fetches stock data, applies a rule-based trading strategy, logs performance to Google Sheets, and includes a bonus machine learning component for predicting stock movements and Telegram integration for real-time alerts.

🎯 Objective
------------

The primary objective is to create a modular and well-documented Python application that automates the end-to-end process of:

*   **Data Ingestion:** Fetching historical stock data from a free API.
    
*   **Strategy Execution:** Applying a technical indicator-based trading strategy.
    
*   **Performance Logging:** Storing and analyzing backtesting results in Google Sheets.
    

### ✨ Bonus Tasks

*   **ML Automation:** A basic Decision Tree classifier is implemented to predict next-day price movement, with its accuracy logged.
    
*   **Telegram Alert Integration:** Real-time alerts are sent to a Telegram chat for key events like backtest completion and ML model accuracy.
    

⚙️ Technologies & Libraries
---------------------------

*   **Python 3.x**
    
*   pandas: For data manipulation and analysis.
    
*   requests: To handle API calls to Alpha Vantage.
    
*   pandas-ta: A powerful library for calculating technical indicators.
    
*   gspread & oauth2client: To authenticate and interact with the Google Sheets API.
    
*   scikit-learn: For the machine learning model (Bonus).
    
*   python-telegram-bot: To send real-time alerts to Telegram (Bonus).
    

🚀 Setup & Installation
-----------------------

Follow these steps to get the project running on your local machine.

### 1\. Clone the Repository

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   git clone   cd algo-trading-prototype   `

### 2\. Set Up the Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Create the virtual environment  python -m venv venv  # Activate the virtual environment  # On macOS/Linux  source venv/bin/activate  # On Windows (Command Prompt)  venv\Scripts\activate.bat  # On Windows (PowerShell)  venv\Scripts\Activate.ps1   `

### 3\. Install Dependencies

Install all the required Python libraries using the requirements.txt file.

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pip install -r requirements.txt   `

### 4\. Configuration

You must configure your API keys and credentials in the config.py file. **Do not upload this file to your public repository after adding sensitive data.**

*   **Alpha Vantage API Key:** Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key).
    
*   **Google Sheets API:**
    
    *   Enable the **Google Sheets API** and **Google Drive API** in the [Google Cloud Console](https://console.cloud.google.com/).
        
    *   Create a **Service Account** and download its JSON key file. Rename it to credentials.json and place it in the project root.
        
    *   Create a new Google Sheet and **share it** with the service account's email address.
        
*   **Telegram Bot (Bonus):**
    
    *   Create a bot with @BotFather and get the **Bot Token**.
        
    *   Find your **numerical Chat ID** by messaging your bot and using the getUpdates API call.
        

Update config.py with your information:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # config.py  ALPHA_VANTAGE_API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY_HERE"  STOCK_SYMBOLS = ["RELIANCE.BSE", "HDFCBANK.BSE", "INFY.BSE"]  GOOGLE_SHEET_KEY_PATH = "credentials.json"  GOOGLE_SHEET_TITLE = "Algo Trading Report"  TELEGRAM_BOT_TOKEN = "YOUR_FULL_TELEGRAM_BOT_TOKEN_HERE"  TELEGRAM_CHAT_ID = "YOUR_NUMERICAL_TELEGRAM_CHAT_ID_HERE"   `

▶️ How to Run
-------------

To run the entire system, execute the main.py script from the project root directory while your virtual environment is active.

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python main.py   `

The script will fetch data, perform the backtest, update the Google Sheet, train the ML model, and send Telegram alerts. Check your terminal logs for detailed progress and your Telegram chat for notifications.

📂 Project Structure
--------------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   /algo_trading_prototype/  |-- venv/  |-- .gitignore  |-- README.md  |-- requirements.txt  |-- main.py  |-- config.py  |-- trading_strategy/  |   |-- __init__.py  |   |-- data_fetcher.py  |   |-- indicators.py  |   |-- backtester.py  |-- sheets_automation/  |   |-- __init__.py  |   |-- sheets_logger.py  |-- ml_model/  |   |-- __init__.py  |   |-- predictor.py  |-- telegram_alerts/      |-- __init__.py      |-- alerter.py   `

✍️ Contribution
---------------

This project is a prototype designed for a specific assignment. Feel free to fork the repository and adapt it for your own use cases.