# Web Scraper Flask App

This project is a Flask web application that allows users to scrape table data from a specified website and download the results as a CSV file.

## Project Structure

```
webscraper-flask-app
├── app.py                # Main entry point of the Flask application
├── scrape.py             # Contains the web scraping logic
├── templates             # Directory for HTML templates
│   └── index.html       # User interface for inputting website links
├── static                # Directory for static files (CSS, JS, images)
├── requirements.txt      # Lists dependencies for the project
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd webscraper-flask-app
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Flask application**:
   ```
   python app.py
   ```

2. **Open your web browser** and go to `http://127.0.0.1:5000`.

3. **Input a website link** in the provided form and submit it to scrape the data.

4. **Download the generated CSV file** from the link provided after the scraping process is complete.

## Dependencies

- Flask
- requests
- beautifulsoup4
- (Any other dependencies used in `scrape.py`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.