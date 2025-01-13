from telegram.ext import ApplicationBuilder
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# 텔레그램 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 토큰 및 채팅 ID 유효성 확인
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")

# 텔레그램 Application 객체 생성
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

async def send_telegram_message(message):
    """
    텔레그램 메시지를 전송하고 전송 결과와 일부 내용을 터미널에 출력합니다.
    """
    try:
        await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        # 메시지 전송 성공 시 결과 출력
        print(f"[텔레그램 메시지 전송 성공] 전송된 메시지 내용 일부: {message[:100]}...")  # 최대 100자 출력
    except Exception as e:
        # 메시지 전송 실패 시 에러 출력
        print(f"[텔레그램 메시지 전송 실패] {e}")