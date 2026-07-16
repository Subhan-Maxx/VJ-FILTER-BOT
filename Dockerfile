# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

FROM python:3.10-slim-bookworm

# सिस्टम पैकेजेस को अपडेट और गिट इंस्टॉल करना
RUN apt update && apt upgrade -y && apt install git -y

# वर्क डायरेक्टरी सेट करना
WORKDIR /VJ-FILTER-BOT

# आवश्यकताओं (requirements) को कॉपी और इंस्टॉल करना
COPY requirements.txt .
RUN pip3 install -U pip && pip3 install --no-cache-dir -U -r requirements.txt

# बाकी के प्रोजेक्ट कोड को कॉपी करना
COPY . .

# बॉट को स्टार्ट करने की कमांड
CMD ["python", "bot.py"]
