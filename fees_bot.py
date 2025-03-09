import sqlite3
import random
import logging
from telegram import Bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ✅ Your Telegram Bot Token
TOKEN = "7830453693:AAFpUu-G1-h52U1qhZu7-HUYF9OVWEKiSD4"

# ✅ Logging setup
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def create_database():
    """📌 Creates a mock database if not exists"""
    conn = sqlite3.connect("fees_data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fees (
                        reg_no TEXT PRIMARY KEY, 
                        reg_number TEXT,
                        name TEXT, 
                        dob TEXT,
                        father_name TEXT,
                        batch TEXT,
                        college TEXT, 
                        department TEXT,
                        year INTEGER,
                        semester TEXT,
                        tuition_fee INTEGER,
                        other_fee INTEGER,
                        hostel_fee INTEGER,
                        paid_fee INTEGER,
                        pending_fee INTEGER)''')

    # ✅ Randomly select 30 hostellers
    total_students = 60
    hostellers = random.sample(range(101, 101 + total_students), 30)

    # ✅ Dummy Data
    student_data = []
    for i in range(101, 101 + total_students):
        reg_no = f'73772218{str(i).zfill(2)}'
        reg_number = f'2022UAM{str(i).zfill(3)}S'
        name = f'Random Name {i}'
        dob = f'200{random.randint(1, 5)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}'
        father_name = f'Father {i}'
        batch = '2022-2026'
        college = 'Random College'
        department = 'Random Dept'
        year = (i % 4) + 1
        semester = f'Sem {(i % 8) + 1}'
        
        tuition_fee = random.randint(40000, 60000)  # Tuition fee for all students
        other_fee = random.randint(5000, 15000)     # Other fee for all students
        hostel_fee = random.randint(25000, 35000) if i in hostellers else 0  # Hostel fee for 30 random students
        paid_fee = random.randint(30000, tuition_fee + other_fee + hostel_fee)
        pending_fee = (tuition_fee + other_fee + hostel_fee) - paid_fee

        student_data.append((reg_no, reg_number, name, dob, father_name, batch, college, department, year, semester,
                             tuition_fee, other_fee, hostel_fee, paid_fee, pending_fee))

    cursor.executemany("""
    INSERT OR IGNORE INTO fees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, student_data)

    conn.commit()
    conn.close()

def log_user(update: Update):
    """📝 Logs users who interact with the bot"""
    user = update.effective_user
    with open("user_logs.txt", "a") as file:
        file.write(f"{user.id}, {user.first_name}, @{user.username}\n")

async def start(update: Update, _):
    """🤖 Greets the user when they start the bot"""
    await update.message.reply_text("Hello! Send me your 11-digit Registration Number to get fee details. 📜")
    log_user(update)

async def handle_message(update: Update, _):
    """📌 Handles registration number validation & fee retrieval"""
    user_input = update.message.text.strip()
    
    if not user_input.isdigit() or len(user_input) != 11:
        await update.message.reply_text("❌ Please enter a valid 11-digit Registration Number!")
        return
    
    conn = sqlite3.connect("fees_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fees WHERE reg_no=?", (user_input,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        reg_no, reg_number, name, dob, father_name, batch, college, dept, year, semester, tuition_fee, other_fee, hostel_fee, paid_fee, pending_fee = result
        response = (f"📛 Name: {name}\n🎂 DOB: {dob}\n👨‍👩‍👦 Father's Name: {father_name}\n🎓 Batch: {batch}\n"
                    f"🏫 College: {college}\n📚 Department: {dept}\n📅 Year: {year}\n📖 Semester: {semester}\n"
                    f"🆔 Reg. Number: {reg_number}\n💰 Tuition Fee: ₹{tuition_fee}\n🧾 Other Fee: ₹{other_fee}\n"
                    f"🏠 Hostel Fee: ₹{hostel_fee}\n✅ Paid: ₹{paid_fee}\n🔴 Pending: ₹{pending_fee}")
    else:
        response = "❌ Registration number not found!"
    
    await update.message.reply_text(response)

async def error_handler(update: object, context: object) -> None:
    logging.error(f"Error: {context.error}")

def main():
    """🚀 Main function to run the bot"""
    create_database()
    bot = Bot(token="YOUR_BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    logging.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
