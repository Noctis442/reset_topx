import telebot
import paramiko
import subprocess

# Replace with your actual Telegram Bot API Token
API_TOKEN = "Your API Token"

# Server information (replace with actual values)
SERVER_IP = "IP_Server"
SERVER_USERNAME = "user"
SERVER_PASSWORD = "password"

# Function to establish SSH connection
def ssh_connect():
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(SERVER_IP, username=SERVER_USERNAME, password=SERVER_PASSWORD)
        return ssh_client
    except paramiko.SSHException as e:
        print(f"SSH connection error: {e}")
        return None

# Create Telegram Bot object
bot = telebot.TeleBot(API_TOKEN)

# Bot status variable
bot_status = "idle"

# Function to send message to user
def send_message(chat_id, message, bot_obj=bot):
    try:
        bot_obj.send_message(chat_id, message)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Telegram API error: {e}")

# Handler for incoming messages
@bot.message_handler(content_types=["text"])
def handle_message(message):
    global bot_status

    if bot_status == "idle":
        # Start bot
        if message.text.lower() == "halo zayyan":
            bot_status = "waiting_ip"
            send_message(message.chat.id, "Hai juga, silahkan masukkan IP Address Client untuk reset TOPX")
    elif bot_status == "waiting_ip":
        # Get IP address
        ip_address = message.text

        # Connect to server via SSH
        ssh_client = ssh_connect()

        # Check for successful connection
        if ssh_client is None:
            send_message(message.chat.id, "Koneksi ke server gagal. Periksa informasi server.")
            return

        # Get process list
        stdin, stdout, stderr = ssh_client.exec_command(f"ps -ef | grep {ip_address}")
        process_list = stdout.read().decode("utf-8")

        # Close SSH connection
        ssh_client.close()

        # Send process list to user
        send_message(message.chat.id, process_list)

        # Change bot status
        bot_status = "waiting_pid"
    elif bot_status == "waiting_pid":
        # Get process ID
        process_id = message.text

        try:
            # Validate process ID (ensure it's an integer)
            int(process_id)
        except ValueError:
            send_message(message.chat.id, "Nomor proses tidak valid. Masukkan angka.")
            return

        # Connect to server via SSH
        ssh_client = ssh_connect()

        # Check for successful connection
        if ssh_client is None:
            send_message(message.chat.id, "Koneksi ke server gagal. Periksa informasi server.")
            return

        # Kill process
        ssh_client.exec_command(f"kill -9 {process_id}")

        # Close SSH connection
        ssh_client.close()

        # Send confirmation message
        send_message(message.chat.id, f"Process dengan ID {process_id} pada server telah dihentikan.")

        # Reset bot status
        bot_status = "idle"
    elif message.text.lower() == "terimakasih":
        # Stop bot
        bot.stop()

# Run the bot
bot.polling()
