import yfinance as yf
from bs4 import BeautifulSoup
import requests



def get_stock_price(ticker, period="1d", interval="5m"):
    """
    Fetch the stock price for a given ticker symbol.

    Parameters:
    - ticker (str): The stock ticker symbol (e.g., "AAPL").
    - period (str): The period of data to retrieve (e.g., "1d", "5d", "1mo", "1y").
    - interval (str): The interval for data points (e.g., "1m", "5m", "1h", "1d").

    Returns:
    - price (float): The last available closing price or None if no data is found.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)

    """
    if not data.empty:
        # Get the last closing price
        price = data['Close'].iloc[-1]
        print(f"The latest closing price of {ticker} is: ${price:.2f}")
        return price
    else:
        print("No data found.")
        return None
    """

    return data[['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']].reset_index().values.tolist()


def get_stock_news(ticker):
    msft = yf.Ticker("MSFT")
    return msft.news


def remove_deepest_paragraph_with_sign_up(p_tag):
    # Check if the current <p> tag has nested <p> tags
    nested_paragraphs = p_tag.find_all('p', recursive=False)  # Only get immediate children <p> tags

    if not nested_paragraphs:  # If there are no nested <p> tags, we're at the deepest level
        # Check if the deepest <p> contains "Sign Up"
        if 'Sign Up' in p_tag.get_text():
            p_tag.decompose()  # Remove this <p> tag
        return

    # If there are nested <p> tags, recursively go through them
    for nested_p in nested_paragraphs:
        remove_deepest_paragraph_with_sign_up(nested_p)


def remove_buttons(tag):
    # If the current tag is a <button>, hide it instead of decomposing for testing
    if tag.name == 'button':
        # Hide button instead of decomposing to check for content loss
        tag['style'] = 'display: none;'  # Just hide it instead of deleting it
        return
    # Otherwise, recursively call the function on all children
    for child in tag.find_all(True, recursive=False):  # Only immediate children
        remove_buttons(child)



def getTextFromNews(news):
    url = news.format('brexit')
    print(url)
    headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
    }
    resp = requests.get(url,headers=headers)


    soup = BeautifulSoup(resp.text,'lxml')
    article = soup.select('div[class*="body-wrap"]')

    paragraphs = soup.find_all("p")
    remove_buttons(soup)

    for p in paragraphs:
        remove_deepest_paragraph_with_sign_up(p)

    content = ""
    for div in article:
        # Get the text, but preserve inline elements like <strong> (bold) or <em> (italic)
        text_content = div.prettify()  # This keeps all the HTML tags intact
        # Replace unnecessary line breaks around inline elements (e.g., bolded text)
        text_content = text_content.replace("\n", "")  # Remove newline characters

        # Optionally, you can replace all occurrences of certain tags with custom styling
        text_content = text_content.replace("<strong>", "<span style='font-weight: bold;'>")
        text_content = text_content.replace("</strong>", "</span>")
        text_content = text_content.replace("View comments", "")

        content += text_content

        content = content.split("Don’t miss this", 1)[0]

    return content

"""

    # Get the parent of the <h2> element
    h2_element = cards[0]
    parent_element = h2_element.parent

    # Find all sibling <div> elements (co-children of <h2>)
    co_children_divs = parent_element.find_all('div', recursive=False)
    co_children_divs = co_children_divs[1]

    # Collect text content from these <div> elements
    content = ''
    for div in co_children_divs:
        text = div.get_text().strip()
        if "Watch the complete interview" in text:
            break

        content += text"""


def getBasicAnalysis(content):
    # Use a pipeline as a high-level helper
    from transformers import pipeline
    sentiment_task = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

    return sentiment_task([content])


# Example usage
#print(getTextFromNews(get_stock_news("MSFT")[0]["link"]))
