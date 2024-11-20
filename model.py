from bs4 import BeautifulSoup
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax


# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)


MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)

model = AutoModelForSequenceClassification.from_pretrained(MODEL)


def getSentimentData(html):

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=" ", strip=True)
    splitText = [""]
    text = text.split(".")

    currentLen = 0
    currentIndex = 0
    for el in text:
        if currentLen + len(el) <= 500:
            currentLen += len(el)
            splitText[currentIndex] += el
        else:
            currentLen = 0
            currentIndex += 1
            splitText.append("")

    overallScore = {}

    for stext in splitText:
        stext = preprocess(stext)
        encoded_input = tokenizer(stext, return_tensors='pt')
        output = model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)

        ranking = np.argsort(scores)
        ranking = ranking[::-1]
        for i in range(scores.shape[0]):
            l = config.id2label[ranking[i]]
            s = scores[ranking[i]]

            if l not in overallScore:
                overallScore[l] = []
            overallScore[l].append(np.round(float(s), 4))

            # print(f"{i + 1}) {l} {np.round(float(s), 4)}")

    for key, value in overallScore.items():
        overallScore[key] = round(sum(value) / len(value), 3)

    return overallScore


"""
t = "Carillon Tower Advisers, an investment management company, released its “Carillon Eagle Growth & Income Fund” third quarter 2024 investor letter. A copy of the letter can be downloaded here. Although the S&P 500 Index had a 5.9% increase in third-quarter trading, the benchmark index ended the first nine months of 2024 with a remarkable 22.1% gain. The exceptional performance was fueled by a strong surge in technology stocks, artificial intelligence trends, and the start of a U.S. Federal Reserve (Fed) rate reduction cycle. In addition, you can check the fund's top 5 holdings to determine its best picks for 2024.Carillon Eagle Growth & Income Fund highlighted stocks like Microsoft Corporation (NASDAQ:MSFT), in the third quarter 2024 investor letter. Microsoft Corporation (NASDAQ:MSFT) is a multinational software company that develops and supports software, services, devices, and solutions. The one-month return of Microsoft Corporation (NASDAQ:MSFT) was 2.09%, and its shares gained 15.42% of their value over the last 52 weeks. On November 14, 2024, Microsoft Corporation (NASDAQ:MSFT) stock closed at $426.89 per share with a market capitalization of $3.174 trillion.Carillon Eagle Growth & Income Fund stated the following regarding Microsoft Corporation (NASDAQ:MSFT) in its Q3 2024 investor letter:Microsoft Corporation (MSFT) traded lower following concerns about the sustainability of its data center buildout for generative artificial intelligence (AI). The company continues to show strong growth in its cloud segment, and management highlighted optimism surrounding demand signals.A development team working together to create the next version of Windows.icrosoft Corporation (NASDAQ:MSFT) is in second position on our list of 31 Most Popular Stocks Among Hedge Funds. As per our database, 279 hedge fund portfolios held Microsoft Corporation (NASDAQ:MSFT) at the end of the second quarter which was 293 in the previous quarter. In the September quarter, Microsoft Corporation’s (NASDAQ:MSFT) revenue was $65.6 billion, up 16% year-over-year and earnings per share was $3.30, representing a 10% increase compared to prior years quarter. While we acknowledge the potential of Microsoft Corporation (NASDAQ:MSFT) as an investment, our conviction lies in the belief that AI stocks hold greater promise for delivering higher returns, and doing so within a shorter timeframe. If you are looking for an AI stock that is as promising as NVIDIA but that trades at less than 5 times its earnings, check out our report about the cheapest AI stock.Story ContinuesIn another article, we discussed Microsoft Corporation (NASDAQ:MSFT) and shared the list of best predictive analytics stocks to invest in. In addition, please check out our hedge fund investor letters Q3 2024 page for more investor letters from hedge funds and other leading investors. READ NEXT: Michael Burry Is Selling These Stocks and A New Dawn Is Coming to US Stocks. Disclosure: None. This article is originally published at Insider Monkey.View Comments"
print(getSentimentData(t))
"""
