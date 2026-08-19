import os
import shutil
import asyncio
from telethon import TelegramClient, events

# اطلاعات خود را وارد کنید
API_ID = 31982008  # عدد بدون کوتیشن
API_HASH = "be22af0eaa0b58d6b30c35d0bb407555"
BOT_TOKEN = "8874637518:AAHvrZMh3OYcY3UPb0ZE4gk6mhQqUSxljOg"
CHANNEL_ID = "@rarextra"  # آیدی کانال مقصد
DRIVE_PATH = "/content/drive/MyDrive/Audio"

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern=None))
async def handler(event):
    # بررسی ارسال فایل با پسوند rar
    if not event.file or not (event.file.name and event.file.name.lower().endswith('.rar')):
        return

    status_msg = await event.reply("📥 در حال دانلود فایل RAR از تلگرام...")
    
    # دانلود بدون قطعی تا ۲ گیگابایت
    rar_path = await event.download_media(file="/content/temp.rar")
    
    await status_msg.edit("⚙️ در حال استخراج محتویات...")
    extract_dir = "/content/temp_extract"
    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(DRIVE_PATH, exist_ok=True)
    
    # اکسترکت در بک‌گراند
    proc = await asyncio.create_subprocess_exec("unrar", "x", "-y", rar_path, extract_dir + "/")
    await proc.communicate()
    
    if os.path.exists(rar_path):
        os.remove(rar_path)

    await status_msg.edit("🎵 در حال فشرده‌سازی با FFmpeg و ارسال به کانال...")
    
    valid_extensions = ('.mp3', '.m4a', '.ogg', '.wav', '.flac', '.aac')
    
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                input_file = os.path.join(root, file)
                base_name = os.path.splitext(file)[0]
                output_file = os.path.join(extract_dir, f"{base_name}_32k.mp3")
                
                # فشرده‌سازی با FFmpeg
                ff = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-i", input_file,
                    "-b:a", "32k", "-map", "a", output_file, "-y",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await ff.communicate()
                
                # ارسال فایل صوتی به کانال
                if os.path.exists(output_file):
                    await bot.send_file(
                        CHANNEL_ID,
                        output_file,
                        caption=f"🎧 {base_name}",
                        voice_note=False
                    )
                    
                    # ذخیره در درایو
                    shutil.copy(output_file, os.path.join(DRIVE_PATH, f"{base_name}_32k.mp3"))
                    os.remove(output_file)
                
                if os.path.exists(input_file):
                    os.remove(input_file)

    shutil.rmtree(extract_dir, ignore_errors=True)
    await status_msg.edit("🎉 تمامی فایل‌ها با موفقیت فشرده، به کانال ارسال و در درایو ذخیره شدند.")

print("ربات روشن است و منتظر ارسال فایل...")
bot.run_until_disconnected()
