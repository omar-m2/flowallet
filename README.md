# Flowallet

A user-friendly personal finance manager desktop application designed to help you track your income and expenses, export and visualize your financial data, and manage your budget efficiently.

## Table of Contents

* [Live Demo](#live-demo)
* [Features](#features)
* [Technologies Used](#technologies-used)
* [How To Use](#how-to-use)
* [How To Run Locally](#how-to-run-locally)
* [Building Executable](#building-executable)
* [Future Improvements](#future-improvements)
* [Project Structure](#project-structure)
* [Contribution](#contribution)
* [License](#license)
* [Authors](#authors)

## Live Demo

Check out the live demo of the application [here](https://www.youtube.com/watch?v=kwnSvVSIPl4).

## Features

* **Transaction Management:** Add, edit, and delete income and expense transactions.
* **Persistent Data Storage:** Transactions are saved locally using SQLite for easy retrieval and analysis.
* **Search Functionality:** Easily search for transactions with real-time filtering.
* **Export Data:** Export your financial data to CSV format for easy sharing and analysis.
* **Data Visualization:** View your financial data through interactive charts (pie and bar charts for each of income and expenses by category and line charts for for monthly trends).
* **User-Friendly Interface:** Intuitive layout for easy navigation.
* **Responsive Design:** Optimized UI for various screen sizes.

## Technologies Used

* **Python:** Main programming language.
* **Tkinter:** GUI framework for creating the application interface.
* **SQLite:** Embedded database system used to store transaction data locally in a structured format.
* **Matplotlib:** Data visualization and analysis library.
* **Ttkbootstrap:** Styling and modern flat themes library.
* **CSV:** Library to import and export data in spreadsheet.
* **Unittest:** Python's built-in framework for writing and running automated tests.
* **PyInstaller:** Tool used for packaging the application into a standalone executable.

## How To Use

* **Open** the application by following the steps in [How To Run Locally](#how-to-run-locally) or [Building Executable](#building-executable)

* **Add** a transaction by:
  * Entering a valid numeric amount in the Amount field.
  * Entering a category name in the Category field.
  * Selecting a transaction type (Income/Expense).
  * Clicking the Add Transaction button or pressing Enter.

* **View** your transaction history by pressing the View Transaction History button. You can search for a specific transaction by type, category, or date using the Search field. The search feature updates live—no need to press any button.

* **Delete** transactions from the Transaction History window by:
  * Selecting a transaction (or multiple transactions by click-and-drag).
  * Pressing the Delete button and confirming deletion.

* **Export** your transactions to a CSV file by clicking the Export Data to CSV button. You can filter the export by type, category, or date by entering a value in one or more of the filter fields.

* **Visualize** your income and expenses by:
  * Viewing pie and bar charts that categorize income and expenses, accessible through the pie and bar charts buttons on the main window.
  * Following monthly trends in a line chart, accessible through the line charts buttons on the main window.

* **Track** your income, expenses, and total balance at the bottom of the main window, updated automatically upon starting the application.

## How To Run Locally

### **Prerequisites**

* Python 3.12.6
* Required libraries: `tkinter`, `numpy`, `matplotlib`, `ttkbootstrap`

### **Steps to Install**

1. **Clone the repository:**

    ```bash
    git clone https://github.com/omar-m2/flowallet
    ```

2. **Navigate to the project directory:**

    ```bash
    cd flowallet
    ```

3. **Install requirements:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the program:**

    ```bash
    python flowallet.py
    ```

5. **If you encounter issues with tkinter, refer to the following installation guide:**

* On Windows, tkinter is included with Python.
* On macOS, install it via Homebrew: brew install python-tk.
* On Ubuntu, use: sudo apt-get install python3-tk.

## Building Executable

To package the application as an executable, follow these steps:

1. **Install PyInstaller:**

    ```bash
    pip install pyinstaller
    ```

2. **Install requirements:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Navigate to the project directory:**

    ```bash
    cd flowallet
    ```

4. **Create the executable:**

    ```bash
    pyinstaller --onefile --windowed --icon=assets/app_logo.ico --add-data "assets/app_logo.ico;assets" --hidden-import matplotlib.backends.backend_tkagg --hidden-import matplotlib.backends.backend_agg flowallet.py
    ```

    **Important:** Make sure the assets/app_logo.ico file is in the correct folder when packaging to ensure the application icon is included in the executable.

5. **Find Your executable:**

    Once PyInstaller finishes, your packaged application will be in the dist/ folder:

       dist/
       └── flowallet.exe

7. **Test the executable:**

    Test the generated executable by running it:

    ./dist/flowallet.exe

    Make sure all functionalities (transactions, charts, etc.) work properly.

**Note:** PyInstaller creates executables for the OS it’s run on. To package for macOS, Linux, or Windows, run PyInstaller on each respective platform.

## Future Improvements

* **Tabbed Interface:** Introduce tabs for smoother navigation between the main window, transaction history, and charts.
* **Editable Transactions:** Allow users to edit transactions directly in the transaction history by clicking on and updating transaction entries.
* **Sorting & Filtering:** Enable users to sort and filter transactions by date, type, category, or amount for better data management.
* **User Accounts:** Implement a user login system to support multiple users, allowing each user to maintain their own transaction records.
* **Dynamic & Interactive Charts:** Allow users to switch between different chart types (pie, bar, line), apply filters, and interact with data points for more detailed insights.
* **Budgeting Feature:** Introduce a budgeting tool where users can set spending limits per category, track their expenses, and receive alerts when exceeding those budgets.
* **Tooltips:** Add informative tooltips to buttons, providing users with helpful explanations without cluttering the UI.
* **Themes:** Provide multiple theme options (light, dark, classic, colored) so users can customize the application's look and feel.
* **Test Coverage:** Expand test cases for additional functions to handle edge cases and ensure full coverage for a more robust application.

## Project Structure

    flowallet/
    ├── flowallet.py 
    ├── tests/ 
    │ └── test_flowallet.py 
    ├── assets/ 
    │ └── app_logo.ico 
    ├── README.md 
    ├── LICENSE.md 
    ├── .gitignore 
    └── requirements.txt

## Contribution

Feel free to fork the repository and submit pull requests. All contributions are welcome! If you'd like to contribute, follow these steps:

**1. Visit the repository:**

* Navigate to the [GitHub repository](https://github.com/omar-m2/flowallet) to fork.

**2. Click on the Fork button:**

* In the top right corner of the page, click the **Fork** button. This will create a copy of the repository in your GitHub account.

**3. Clone your forked repository:**

* Open your terminal (or Git Bash) and run the following command, replacing YOUR_USERNAME with your GitHub username:

    ```bash
    git clone https://github.com/YOUR_USERNAME/flowallet.git
    ```

* This will create a local copy of the repository on your machine.

**4. Create a new branch:**

* Navigate into the cloned directory:

    ```bash
    cd flowallet
    ```

* Create a new branch for your changes:

    ```bash
    git checkout -b my-feature-branch
    ```

**5. Make your changes:**

* Use your preferred text editor or IDE to edit the files you want to modify

**6. Add and commit your changes:**

* Once you've made your changes, add them to the staging area:

    ```bash
    git add .
    ```

* Commit your changes with a clear, descriptive message:

    ```bash
    git commit -m "Description of changes made"
    ```

**7. Push your changes to GitHub:**

* Push your changes to your forked repository:

    ```bash
    git push origin my-feature-branch
    ```

**8. Create a Pull Request:**

* Go back to the original repository on GitHub. You should see a prompt to create a pull request for your recently pushed branch. Click on Compare & pull request.
* Provide a description of your changes and click Create pull request.

**9. Review and Discuss:**

* Collaborate with the maintainers and other contributors by discussing your pull request. Be prepared to make any necessary changes if requested.

**10. Merge your Pull Request:**

* Once your pull request is approved, it can be merged into the main branch of the original repository.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Authors

Omar Mostafa - [omar.m.abdelhakim@gmail.com](mailto:omar.m.abdelhakim@gmail.com)
