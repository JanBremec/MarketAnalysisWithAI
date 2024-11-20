import re
import streamlit as st
import datetime
import summarizeModel as sM
import getData
import model as mod
import plotly.graph_objects as go

st.set_page_config(initial_sidebar_state="expanded")
newsArticles = getData.get_stock_news("Any")

currentLink = None
#dict_keys(['uuid', 'title', 'publisher', 'link', 'providerPublishTime', 'type', 'thumbnail', 'relatedTickers'])
sidebar_placeholder = st.sidebar.empty()
st.title("Today's Market Analysis")
st.markdown(
    """<div style=" background-color: #f9f9f9; padding: 10px; border-radius: 5px; border: 1px solid #ddd; font-size: 
    14px; color: #333; "> <strong>Disclaimer:</strong> This website is designed for educational purposes 
    only and may contain inaccurate predictions or data. Users are advised not to base financial decisions solely on 
    the information provided here. The platform is powered by advanced machine learning models and multiple APIs, 
    and while efforts are made to ensure accuracy and timeliness, it remains a work in progress. </div>""" ,
    unsafe_allow_html=True
)
if "sidebar_stock" not in st.session_state:
    st.session_state.sidebar_stock = None  # Initialize it if not present

if "sidebar_mode" not in st.session_state:
    st.session_state.sidebar_mode = "standby"  # Modes: "stock", "news", "standby"

if st.session_state.sidebar_mode == "standby":
    with sidebar_placeholder.container():
        # Create dynamic columns with different widths
        columns = st.columns([1, 4, 1])

        # Center the message in the middle column
        with columns[1]:
            # Show a friendly, styled message with an icon
            st.markdown(
                "<h2 style='color: black; font-size: 24px;'>Analysis on stand-by...</h2>",
                unsafe_allow_html=True
            )
            st.write(
                "🔍 You can select an article or a stock to analyze!"
            )

            # Optional: Add more guidance or interactivity suggestions
            st.markdown(
                "<p style='color: gray;'>Once you choose, the analysis will start!</p>",
                unsafe_allow_html=True
            )

            st.image("image.png")


def mini_chart(data):
    start_price = data['Close'][0]  # Get the starting price
    fig = go.Figure()

    # Create the line segments based on price movement
    x_values = list(range(len(data['Close'])))
    current_segment_x = [x_values[0]]  # Starting point
    current_segment_y = [data['Close'][0]]  # Starting price point
    current_color = 'green' if data['Close'][0] >= start_price else 'red'

    # Iterate through the rest of the data points
    for i in range(1, len(data['Close'])):
        if (data['Close'][i] >= start_price and current_color == 'red') or (data['Close'][i] < start_price and current_color == 'green'):
            # Create a trace for the previous segment
            fig.add_trace(go.Scatter(
                x=current_segment_x,
                y=current_segment_y,
                mode='lines',
                line=dict(color=current_color),
                showlegend=False
            ))

            # Start a new segment
            current_segment_x = [x_values[i-1], x_values[i]]
            current_segment_y = [data['Close'][i-1], data['Close'][i]]
            current_color = 'green' if data['Close'][i] >= start_price else 'red'
        else:
            # Continue the current segment
            current_segment_x.append(x_values[i])
            current_segment_y.append(data['Close'][i])

    # Add the last segment
    if current_segment_x:
        fig.add_trace(go.Scatter(
            x=current_segment_x,
            y=current_segment_y,
            mode='lines',
            line=dict(color=current_color),
            showlegend=False
        ))

    # Add the horizontal line at the start price
    fig.add_shape(
        type="line",
        x0=0, x1=len(data['Close'])-1,  # Line across the entire X-axis
        y0=start_price, y1=start_price,  # Line at the starting price level
        line=dict(color="gray", dash="dash")  # Customize line style and color
    )

    # Update layout to adjust chart's look
    fig.update_layout(
        height=50, width=150,  # Small size for mini chart
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),  # Hide x-axis
        yaxis=dict(visible=False),  # Hide y-axis
    )

    return fig


# Dashboard layout
st.header("Market Dashboard")

tabs = st.tabs(["US", "Europe", "Commodities"])
markets = {
    "US": {
        "NVIDIA": "^NVDA",
        "Tesla": "^TSLA",
        "Apple": "^AAPL",
        "Amazon": "^AMZN",
        "Microsoft":"^MSFT"
    },
    "Europe": {
        "Ferrari": "^RACE",
        "Spotify Tehnology": "^SPOT",
        "Novartis": "^NVS"
    },
    "Commodities": {
        "Gold": "^GOLD",
        "Copper": "^SCCO",
        "Crude Oil Brent": "^BZ=F",
        "Silver": "^SI=F"
    }
}


# Inside the loop where you handle each stock and its display:
for i, region in enumerate(["US", "Europe", "Commodities"]):
    with tabs[i]:
        st.subheader(region + " Market")
        st.divider()
        for index, ticker in markets[region].items():
            rawData = getData.get_stock_price(ticker[1:], period="1mo", interval="1d")

            # Stock price data
            firstPrice = rawData[0][1]
            currentPrice = rawData[-1][1]
            openPrices = [el[1] for el in rawData]
            diff = currentPrice - firstPrice

            price, change, change_percent, data = [currentPrice, diff, round(diff/currentPrice * 100, 2), {"Close": openPrices}]
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

            change_color = "red"
            if change > 0:
                change_color = "green"

            col1.markdown(f"**{index}**")
            col2.markdown(
                f"<span style='color:{change_color};'>{price:.2f}  \n{change:+.2f} ({change_percent:+.2f}%)</span>",
                unsafe_allow_html=True)

            conf = {
                'scrollZoom': False,
                'displayModeBar': False,  # Hides the toolbar
                'showTips': False  # Disables tooltips
            }
            col3.plotly_chart(mini_chart(data), use_container_width=True, key=f"chart_{index}", config=conf)

            st.divider()
            if col4.button("->", key=index):
                # Update session state to stock mode
                sidebar_placeholder.empty()

                st.session_state.sidebar_mode = "stock"
                st.session_state.sidebar_stock = ticker[1:]  # Save selected stock ticker
                st.session_state.selected_article = ""



def displayNews(article):
    card_html = f"""
    <div style="
        padding: 20px;
        border-radius: 10px;
        background-color: #f9f9f9;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border: 1px solid #ddd;
        margin-bottom: 20px; /* Added bottom margin */
    ">
        <h3>News Article</h3>
        <p style="font-size: 16px;">{article}</p>
    </div>
    """
    # Display the card using markdown
    st.markdown(card_html, unsafe_allow_html=True)




def showSideBarAnalysis(selectedArticle):
    sidebar_placeholder.empty()
    with sidebar_placeholder.container():
        st.header("Analysis")
        neutral = int(analysis["neutral"] * 100)
        positive = int(analysis["positive"] * 100)
        negative = int(analysis["negative"] * 100)

        # HTML and CSS for the card layout
        card_html = f"""
            <style>
                .card-container {{
                    display: flex;
                    justify-content: space-between;
                    margin-top: 20px;
                }}
                .card {{
                    padding: 20px;
                    border-radius: 10px;
                    width: 30%;
                    color: #fff;
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                    font-family: Arial, sans-serif;
                    transition: transform 0.3s;
                }}
                .card:hover {{
                    transform: scale(1.05);
                }}
                .neutral {{ background-color: #6c757d; }}
                .positive {{ background-color: #28a745; }}
                .negative {{ background-color: #dc3545; }}
                .card-title {{
                    font-size: 1.2em;
                    font-weight: bold;
                }}
                .card-percentage {{
                    font-size: 1.8em;
                    font-weight: bold;
                }}
            </style>
        
            <div class="card-container">
                <div class="card neutral">
                    <div class="card-title">Neutral</div>
                    <div class="card-percentage">{neutral}%</div>
                </div>
                <div class="card positive">
                    <div class="card-title">Positive</div>
                    <div class="card-percentage">{positive}%</div>
                </div>
                <div class="card negative">
                    <div class="card-title">Negative</div>
                    <div class="card-percentage">{negative}%</div>
                </div>
            </div>
        """

        # Data for the chart
        labels = ['Positive', 'Neutral', 'Negative']
        values = [positive, neutral, negative]  # Example values

        # Create the donut chart
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5)])

        # Use a pastel color palette for a friendlier look
        colors = ['#8ecae6', '#ffb703', '#fb8500']

        # Create the donut chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.6,  # Make the hole larger for a modern look
            marker=dict(colors=colors, line=dict(color='#ffffff', width=2))
        )])

        # Customize the layout for a sleek, modern appearance
        fig.update_traces(
            hoverinfo='label+percent',
            textinfo='percent',
            textfont_size=16,
            textfont_color='#333333',
        )

        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=20, b=20, l=20, r=20),
            #paper_bgcolor='#f7f7f7',
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Our score for this article:")
        currentScore = round(positive * 1.1 - negative * 0.9 + 0.5 * neutral, 1)
        co1, co2, co3 = st.columns([2, 1, 2])  # This makes the middle column larger
        # Place the metric in the center column
        with co2:
            st.metric("", currentScore, round(currentScore - 50, 1))

        st.subheader("Summary:")
        styles = st.tabs(["Style 1", "Style 2"])
        summarizedText = sM.getSummarization(selectedArticle)[0]["summary_text"]

        with styles[0]:
            for el in re.split(r'\.\s(?=[A-Z])', summarizedText):
                if len(el) > 0:
                    st.write(f"- {el}.")

        with styles[1]:
            st.write(summarizedText)

        st.subheader("Related Tickers:")
        for t in newsArticles[0]["relatedTickers"]:
            st.write(f"- {t}")


index = 0
st.header("News")
for el in newsArticles:
    imageColumns = st.columns([2, 3, 2, 1])
    with imageColumns[0]:
        try:
            st.image(el["thumbnail"]["resolutions"][0]["url"], use_column_width=True)

        except KeyError:
            st.write("Cannot display Image")

    with imageColumns[1]:
        styled_text = f"""
        <div style="font-size: 15px; font-family: Arial, sans-serif; font-weight: normal; color: black;">
            {el["title"]}
        </div>
        """

        # Displaying the styled text
        st.markdown(styled_text, unsafe_allow_html=True)

    with imageColumns[2]:
        st.write(f"**{el['publisher']}**")
        st.write(datetime.datetime.utcfromtimestamp(el["providerPublishTime"]))

    with imageColumns[3]:
        if st.button("Read", str(index)):
            sidebar_placeholder.empty()
            st.session_state.selected_article = index
            st.session_state.sidebar_mode = ""

    # Check if the current article is the selected one to display details immediately after the button
    if "selected_article" in st.session_state and st.session_state.selected_article == index:
        st.session_state.sidebar_mode = ""
        st.markdown("---")  # Optional divider for better visual separation
        # Fetch and display news content inline
        news = getData.getTextFromNews(newsArticles[index]["link"])
        currentLink = newsArticles[index]["link"]
        analysis = mod.getSentimentData(news)
        displayNews(news)
        st.link_button("Read more...", newsArticles[index]["link"])
        showSideBarAnalysis(news)

    index += 1
    st.divider()

st.markdown(
    """
    <hr style="border: 1px solid #ddd; margin: 20px 0;">
    <div style="
        text-align: center;
        font-family: Arial, sans-serif;
        font-size: 14px;
        color: #555;
        line-height: 1.6;
    ">
        <p><strong>© 2024 Jan Bremec. All rights reserved.</strong></p>
        <p>
            This website is a product of <strong>Jan Bremec</strong>'s efforts to explore and share insights in 
            <em>Financial Analysis Powered by Machine Learning Models</em>. For inquiries, feedback, or collaborations, feel free to reach out.
        </p>
        <p style="margin-top: 10px; font-size: 12px; color: #888;">
            Thank you for visiting!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.sidebar_mode == "stock":
    if st.session_state.sidebar_stock:
        sidebar_placeholder.empty()  # Clear previous sidebar content
        with sidebar_placeholder.container():
            ticker = st.session_state.sidebar_stock
            # Fetch stock data and display in the sidebar
            rawData = getData.get_stock_price(ticker, period="1y", interval="1d")
            firstPrice = round(rawData[0][1], 2)
            currentPrice = round(rawData[-1][1], 2)
            openPrices = [el[1] for el in rawData]
            volume = [el[5] for el in rawData]
            highPrice = round(max(openPrices), 2)
            lowPrice = round(min(openPrices), 2)
            diff = currentPrice - firstPrice
            data = openPrices
            price = currentPrice

            st.sidebar.title(f"Stock Analysis ({ticker})")
            st.sidebar.subheader("Price Chart")
            st.sidebar.line_chart(data, x_label="Days", y_label="Price ($)")
            st.sidebar.divider()

            st.sidebar.subheader("Volume Chart")
            st.sidebar.line_chart(volume, x_label="Days", y_label="Volume")
            st.sidebar.divider()

            columns = st.sidebar.columns([1, 1, 1])
            with columns[0]:
                st.metric("High Price", highPrice, round(price - highPrice, 2))
            with columns[1]:
                st.metric("Price", price, round(diff, 2))
            with columns[2]:
                st.metric("Low Price", lowPrice, round(price - lowPrice, 2))

            st.sidebar.divider()

            # Calculate price change and volatility
            price_change_percent = (currentPrice - firstPrice) / firstPrice * 100
            price_volatility = (highPrice - lowPrice) / firstPrice * 100

            # Calculate the volume growth (percentage increase in volume over the period)
            volume_growth = (volume[-1] - volume[0]) / volume[0] * 100

            # Calculate the price relative to the high (how close is the current price to the highest price)
            price_to_high_ratio = (currentPrice - lowPrice) / (highPrice - lowPrice) * 100

            # Combining the factors into a score:
            score = (price_change_percent * 0.4) + (price_volatility * -0.3) + (volume_growth * 0.2) + (
                        price_to_high_ratio * 0.1)

            score = max(-100, min(100, score))

            # Display the score in the sidebar
            columns = st.sidebar.columns([1, 1, 1])

            with columns[1]:
                if score > 80:
                    status = "Good"
                elif score > 50:
                    status = "Neutral"
                else:
                    status = "Bad"
                st.metric("Score:", status, round(score, 2))

        st.sidebar.info("""
        Combining the factors into a score:
        - Positive price change is weighted heavily (40%)
        - Price volatility (how much the stock fluctuates) negatively impacts the score (-30%)
        - Volume growth contributes positively (20%)
        - How close the price is to the high price contributes positively (10%)
        """)