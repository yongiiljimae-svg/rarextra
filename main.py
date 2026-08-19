import os
import subprocess
import shutil
from pyrogram import Client, filters

# اطلاعات ربات و اکانت خود را اینجا جایگذاری کنید
API_ID = 31982008  # به صورت عدد
API_HASH = "be22af0eaa0b58d6b30c35d0bb407555"
BOT_TOKEN = "8874637518:AAHvrZMh3OYcY3UPb0ZE4gk6mhQqUSxljOg"
CHANNEL_ID = "@rarextra"  # آیدی کانال شما
DRIVE_PATH = "/content/drive/MyDrive/Audios" # مسیر ذخیره در گوگل درایو

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.document | filters.audio)
async def process_rar(client, message):
    if not message.document or not message.document.file_name.endswith('.rar'):
        return

    msg = await message.reply("📥 در حال دانلود فایل RAR از تلگرام...")
    
    # دانلود فایل (پشتیبانی تا ۲ گیگابایت)
    rar_path = await message.download()
    
    await msg.edit("⚙️ دانلود تمام شد. در حال استخراج...")
    extract_dir = os.path.join(os.path.dirname(rar_path), "extracted")
    os.makedirs(extract_dir, exist_ok=True)
    
    # استخراج فایل با unrar
    subprocess.run(["unrar", "x", "-y", rar_path, extract_dir + "/"])
    
    # ایجاد پوشه در گوگل درایو (در صورت عدم وجود)
    os.makedirs(DRIVE_PATH, exist_ok=True)
    
    await msg.edit("✅ استخراج انجام شد. در حال فشرده‌سازی و ارسال به کانال...")
    
    valid_extensions = ('.mp3', '.m4a', '.ogg', '.wav')
    
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                input_file = os.path.join(root, file)
                
                # تغییر نام فایل خروجی برای جلوگیری از تداخل و تعیین فرمت mp3
                base_name = os.path.splitext(file)[0]
                output_file = os.path.join(extract_dir, f"{base_name}_32k.mp3")
                
                # فشرده‌سازی صوت به 32kbps با FFmpeg
                subprocess.run([
                    "ffmpeg", "-i", input_file, 
                    "-b:a", "32k", "-map", "a", output_file, "-y"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # ارسال به کانال
                await client.send_audio(CHANNEL_ID, output_file)
                
                # کپی در گوگل درایو
                shutil.copy(output_file, os.path.join(DRIVE_PATH, f"{base_name}_32k.mp3"))

    # پاکسازی فایل‌های موقت از فضای کولب برای جلوگیری از پر شدن حافظه
    os.remove(rar_path)
    shutil.rmtree(extract_dir)
    
    await msg.edit("🎉 تمامی فایل‌ها با موفقیت فشرده، ارسال و در درایو ذخیره شدند.")

app.run()
