import pandas as pd
import requests
import time
import ast
import datetime
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
QDT_POOL_ADDRESS = os.environ.get("QDT_POOL_ADDRESS")
CHECK_EVERY_SECONDS = int(os.environ.get("CHECK_EVERY_SECONDS", 5))


def get_with_retry(url, max_retries=3, delay=1):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            else:
                logger.error(f"Error: HTTP status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error: {e}")       
        retries += 1
        time.sleep(delay)
    return None

def send_message(message):
    send_text = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage?chat_id=" + TELEGRAM_CHAT_ID + "&parse_mode=Markdown&text=" + message
    response = get_with_retry(send_text)
    if response:
        return response
    else:
        logger.error("ERROR in sending message, wait for the next monitor cycle!")


def check_new_transactions(data_df, init_transaction):
    if data_df.iloc[0]["hash"] != init_transaction:
        logger.info("NEW TRANSACTION! Sending message")
        new_df = data_df[data_df["hash"] == data_df.iloc[0]["hash"]]
        token0 = new_df.iloc[0]["tokenSymbol"]
        token1 = new_df.iloc[1]["tokenSymbol"][1:] if new_df.iloc[1]["tokenSymbol"] == "WETH" else new_df.iloc[1]["tokenSymbol"]
        value0 = ast.literal_eval(new_df.iloc[0]["value"])/1e18
        value1 = ast.literal_eval(new_df.iloc[1]["value"])/1e18
        utc_datetime = datetime.datetime.fromtimestamp(int(new_df.iloc[0]["timeStamp"]), datetime.timezone.utc)
        utc_date_string = utc_datetime.strftime("%b-%d-%Y %I:%M:%S %p +UTC")
        message = "*Nuova transazione*"
        message += f"\nHash: {data_df.iloc[0]['hash']}"
        message += f"\nDate: {utc_date_string}"
        message += f"\nSwap: {value0} {token0} \U000027A1 {value1} {token1}"
        send_message(message)
        return data_df.iloc[0]["hash"]

    
def new_transactions_monitor(init_transaction):
    url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={QDT_POOL_ADDRESS}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    response = get_with_retry(url)

    if response:
        data = response.json()
        data_df = pd.DataFrame(data["result"])
        new_tr = check_new_transactions(data_df, init_transaction)
        return new_tr
    else:
        send_message("Unable to call Etherscan!")

if __name__=="__main__":
    init_transaction = "0x0"
    while True:
        new_tr = new_transactions_monitor(init_transaction)
        if new_tr:
            init_transaction = new_tr
        else:
            logger.debug(f"NO new transactions in the last {CHECK_EVERY_SECONDS} seconds")
        time.sleep(CHECK_EVERY_SECONDS)
