# DEX-transactions-telegram

1. docker build -t transactions-check .
2. docker run -d --name transactions-check -e TELEGRAM_BOT_TOKEN="XXXXXX" \
           -e TELEGRAM_CHAT_ID="1234" \
           -e ETHERSCAN_API_KEY="XXXXXX" \
           -e QDT_POOL_ADDRESS="0x00000" \
           -e CHECK_EVERY_SECONDS=3600 \
           transactions-check