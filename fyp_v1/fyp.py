import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from deployment import * 

# Page title
st.set_page_config(
    page_title="Stock Strategy Planning",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded")

# Show header
st.title("Stock")

# Creating sidebar
sideb = st.sidebar

sideb.header("User Input Parameter")
sb = sideb.selectbox(
    'Select Type',
     ['Airasia Stock','Bitcoin']
     )

@st.cache(allow_output_mutation=True)

def display_stock_data():
    presentable_data = pd.DataFrame()
    found = True
    day=1
    while presentable_data.empty and day <7:
        ytd = date.today() - timedelta(days = day)
        presentable_data = yf.download(stock_symbol, ytd, date.today(), auto_adjust=True)
        day = day+1

        if day == 7:
            found = False

    return presentable_data, found

if sb=='Airasia Stock':
    checkSharePrice(getCurrentDate())
    location = './realtimeData.csv'
    df_full = pd.read_csv(location, header=None ,names=['Date', 'Open', 'High', 'Low', 'Volume', 'Close', 'KLCI', 'Pos', 'Neu', 'Neg', 'dr', 'f02', 'Vol Log', 'diff', 'diff50', 'roc', 'ma_5', 'ma_200', 'ema_50'])
    model = PPO.load("./models/PPO/B5")
    envPred =  StockTradingEnv(df_full)
    obs = envPred.reset()
    for i in range(len(df_full['Date'])):
        action, _states = model.predict(obs)
        obs, rewards, done, info, buyList, sellList = envPred.step(action)
    buy = buyList
    sell = sellList
    resultAction = 'hold'
    color = 'Gray'
    if(buy[-1] is not None):
        resultAction = 'Buy'
        color = 'Green'
    elif(sell[-1] is not None):
        resultAction = 'Sell'
        color = 'Red'
    
    df_full['action'] = np.nan
    for i in range(len(buy)):
        if(buy[i] is not None):
            df_full['action'][i] = 1
        elif(sell[i] is not None):
            df_full['action'][i] = -1

    fig = go.Figure(data=[go.Candlestick(x=df_full['Date'],
                open=df_full['Open'],
                high=df_full['High'],
                low=df_full['Low'],
                close=df_full['Close']
                )])

    buyList = df_full.loc[df_full['action']==1]
    sellList = df_full.loc[df_full['action']==-1]
    fig.add_trace(go.Scatter(x=buyList['Date'], y=buyList['Close'],
                    mode='markers', marker=dict(color="green", size=9), marker_symbol='triangle-up'))
    fig.add_trace(go.Scatter(x=sellList['Date'], y=sellList['Close'],
                    mode='markers', marker=dict(color="red", size=9), marker_symbol='triangle-down'))
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    msg = '<p style="font-family:sans-serif; color:{}; font-size: 18px;"><strong>{}</strong></p>'.format(color, resultAction)
    st.markdown(msg, unsafe_allow_html=True)


    

    


    