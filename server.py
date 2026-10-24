import re
import asyncio
from aiohttp import web
from pyrogram import Client

# بيانات الربط
API_ID = 37842426
API_HASH = "14cee7ede734b76a7bc8edc0f2a4dc5b"
BOT_TOKEN = "8723510461:AAG6sKoiUgTXN9ZWC60VcDD2U6qDvlhelrM" # استبدل هذا بالتوكن الخاص بك من BotFather
CHANNEL_ID = -10052504489 # معرف القناة الخاص بك

bot = Client("george_platform_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def stream_handler(request):
    message_id = int(request.match_info.get('message_id'))
    message = await bot.get_messages(CHANNEL_ID, message_id)
    
    if not message or not message.video:
        return web.Response(status=404, text="الفيديو غير موجود")

    file_size = message.video.file_size
    range_header = request.headers.get('Range', 'bytes=0-')
    
    match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    start = int(match.group(1))
    end = int(match.group(2)) if match.group(2) else file_size - 1
    
    headers = {
        'Content-Type': 'video/mp4',
        'Accept-Ranges': 'bytes',
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Content-Length': str(end - start + 1),
    }
    
    response = web.StreamResponse(status=206, headers=headers)
    await response.prepare(request)
    
    # سحب أجزاء الفيديو من تيليجرام وبثها للمشغل
    async for chunk in bot.stream_media(message, offset=start, limit=(end - start + 1)):
        await response.write(chunk)
        
    return response

async def start_server():
    await bot.start()
    app = web.Application()
    app.router.add_get('/stream/{message_id}', stream_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print("السيرفر يعمل الآن... يمكنك تجربة الرابط: http://localhost:8080/stream/رقم_الرسالة")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_server())