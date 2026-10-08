import telebot
import re
import requests
import time
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from functions import insertUser, track_exists, addBalance, cutBalance, getData, addRefCount, isExists, setWelcomeStaus, setReferredStatus

bot_token = "8864390091:AAH7YTytzBl8QuckSa_whUq_Vj2kWakOLcQ" #bot token from @BotFather
SmmPanelApi = "https://panel.telegramboost.shop/api/v2" # api key from eadysmmpanel.com you can change api link
bot = telebot.TeleBot(bot_token)
admin_user_id = 8591379261
welcome_bonus = 100
ref_bonus = 500
min_view = 100
max_view = 30000
required_channels = ['@pythonViewbooster']  # more channel same as
payment_channel = "@pythonViewbooster"


# Function to check if the user is a member of all required channels
def is_member_of_channel(user_id):
  for channel in required_channels:
    status = bot.get_chat_member(channel, user_id).status
    if status not in ['member', 'administrator', 'creator']:
      return False
  return True


@bot.message_handler(commands=['start'])
def send_welcome(message):
  user_id = str(message.from_user.id)
  first_name = message.from_user.first_name
  ref_by = message.text.split()[1] if len(
      message.text.split()) > 1 and message.text.split()[1].isdigit() else None

  # bot.reply_to(message, f"ref_by: {ref_by}")

  if ref_by and int(ref_by) != int(user_id) and track_exists(ref_by):
    if not isExists(user_id):
      initial_data = {
          "user_id": user_id,
          "balance": 0.00,
          "ref_by": ref_by,
          "referred": 0,
          "welcome_bonus": 0,
          "total_refs": 0,
      }
      insertUser(user_id, initial_data)
      addRefCount(ref_by)

  if not isExists(user_id):
    initial_data = {
        "user_id": user_id,
        "balance": 0.00,
        "ref_by": "none",
        "referred": 0,
        "welcome_bonus": 0,
        "total_refs": 0,
    }

    insertUser(user_id, initial_data)

  if not is_member_of_channel(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("/start")

    markup.add(button1)

    bot.send_message(
        user_id,
        "You need to join the following channels before continuing:\n- @pythonViewbooster",
        parse_mode='HTML',
        reply_markup=markup  # Pass the markup to the reply
    )
    return

  userData = getData(user_id)
  # userData = json.loads(userData)
  wel = userData['welcome_bonus']
  if wel == 0:
    bot.send_message(user_id, f"+{welcome_bonus} coins as welcome bonus.")
    addBalance(user_id, welcome_bonus)
    setWelcomeStaus(user_id)

  data = getData(user_id)
  refby = data['ref_by']
  referred = data['referred']
  if refby != "none" and referred == 0:
    bot.send_message(refby, f"you referred {first_name} +{ref_bonus}")
    addBalance(refby, ref_bonus)
    setReferredStatus(user_id)

  markup = ReplyKeyboardMarkup(resize_keyboard=True)
  button1 = KeyboardButton("👁‍🗨 Order View")
  button2 = KeyboardButton("👤 My Account")
  button3 = KeyboardButton("💳 Pricing")
  button4 = KeyboardButton("🗣 Invite Friends")
  button5 = KeyboardButton("📜 Help")

  markup.add(button1)
  markup.add(button2, button3)
  markup.add(button4, button5)
  bot.reply_to(
      message,
      """With view booster bot there's just a few steps to increase the views of your Telegram posts.

👇🏻 To continue choose an item""",
      reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
  user_id = message.chat.id
  bot_username = bot.get_me().username
  first_name = message.chat.first_name

  # balance command
  if message.text == "👤 My Account":
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    data = getData(user_id)
    total_refs = data['total_refs']
    balance = data['balance']
    msg = f"""<b><u>My Account</u></b>

🆔 User id: {user_id}
👤 Username: @{message.chat.username}
🗣 Invited users: {total_refs}
🔗 Referral link: {referral_link}

👁‍🗨 Balance: <code>{balance}</code> Views
"""
    bot.reply_to(message, msg, parse_mode='html')

  if message.text == "🗣 Invite Friends":
    bot_username = bot.get_me().username  # Get the bot's username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    data = getData(user_id)
    total_refs = data['total_refs']

    bot.reply_to(
        message,
        f"<b>Referral link:</b> {referral_link}\n\n<b><u>Share it withfriends and get {ref_bonus} coins for each referral</u></b>",
        parse_mode='html')

  if message.text == "📜 Help":
    msg = f"""<b><u>❓ Frequently Asked questions</u></b>

<b><u>•Are the views real?</u></b>
No, the views are completely fake and no real observations are made.

<b><u>•What is the minimum and maximum views order for a single post?</u></b>
The minimum and maximum views order for a post is {min_view} and {max_view} views, respectively.

<b><u>•Is it possible to register a channel and view automatically?</u></b>
Yes, first set the bot as your channel admin and then register your channel in the bot and specify the amount of views. As soon as a post is published on your channel, the view starts automatically.

<b><u>•What is the average speed of views?</u></b>
Estimating views speed is difficult because the speed can vary depending on the network status and the amount of orders, but on average 40 to 80 views per minute is possible for one post.

<b><u>•How to increase your credit?</u></b>
1- Invite your friends to Bot, for each invitation, {ref_bonus} free views will be added to your account and {welcome_bonus} to your invited user.
2- Buy one of the views packages. We accept PayPal, Paytm, WebMoney, Perfect Money, Payeer, Bitcoin, Tether and other Cryptocurrencies.

<b><u>•Is it possible to transfer balance to other users?</u></b>
Yes, if your balance is more than 10k and you want to transfer all of them, you can send a request to support.

🆘 In case you have any problem, contact @KsCoder"""

    bot.reply_to(message, msg, parse_mode="html")

  if message.text == "💳 Pricing":
    msg = f"""<b><u>💎 Pricing 💎</u></b>

<i>👉 Choose one of the views packages and pay its cost via provided payment methods.</i>

<b><u>📜 Packages:</u></b>
<b>➊ 📦 75K views for 5$ (0.07$ per K)
➋ 📦 170K views for 10$ (0.06$ per K)
➌ 📦 400K views for 20$ (0.05$ per K)
➍ 📦 750K views for 30$ (0.04$ per K)
➎ 📦 1700K views for 50$ (0.03$ per K)
➏ 📦 5000K views for 100$ (0.02$ per K) </b>

💰 Pay with Bitcoin, USDT, BSC, BUSD,  ... 👉🏻 @KsCoder

💳️ Pay with Paypal, Paytm, WebMoney, Perfect Money, Payeer ... 👉🏻 @KsCoder

<b><u>🎁 Bonus:</u></b>
Cryptocurrency: 10%
Payeer and Perfect Money: 5%
Other methods: 0%

<b>🆔 Your id:</b> <code>{user_id}</code>
"""

    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("💲 PayPal", url="https://t.me/KsCoder")
    button2 = InlineKeyboardButton("💳 Perfect Money",
                                   url="https://t.me/KsCoder")
    button6 = InlineKeyboardButton("💳 Webmoney", url="https://t.me/KsCoder")
    button3 = InlineKeyboardButton("💎 Bitcoin, Litecoin, USDT...",
                                   url="https://t.me/KsCoder")
    button4 = InlineKeyboardButton("💸 Paytm", url="https://t.me/KsCoder")
    button5 = InlineKeyboardButton("💰 Paytm", url="https://t.me/KsCoder")

    markup.add(button1)
    markup.add(button2, button6)
    markup.add(button3)
    markup.add(button4, button5)

    bot.reply_to(message, msg, parse_mode="html", reply_markup=markup)

  if message.text == "👁‍🗨 Order View":

    data = getData(user_id)
    balance = data['balance']

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("✘ Cancel")
    markup.add(button1)

    msg = f"""👉‍ Enter number of Views in range ({min_view}, {max_view}) 👇🏻

👁‍🗨️ Your balance: {balance} views
"""
    bot.reply_to(message, msg, reply_markup=markup, parse_mode="html")
    bot.register_next_step_handler(message, view_amount)


markup = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton("👁‍🗨 Order View")
button2 = KeyboardButton("👤 My Account")
button3 = KeyboardButton("💳 Pricing")
button4 = KeyboardButton("🗣 Invite Friends")
button5 = KeyboardButton("📜 Help")
markup.add(button1)
markup.add(button2, button3)
markup.add(button4, button5)


def view_amount(message):
  user_id = message.from_user.id
  if message.text == "✘ Cancel":
    bot.reply_to(message,
                 "Operation successfully canceled.",
                 reply_markup=markup)
    return

  amount = message.text
  data = getData(str(user_id))
  bal = data['balance']

  if not amount.isdigit():
    bot.send_message(user_id,
                     "📛 Invalid value. Enter only numeric value.",
                     parse_mode="Markdown",
                     reply_markup=markup)
    return
  if int(amount) < min_view:
    bot.send_message(user_id,
                     f"❌ Minimum - {min_view} Views",
                     parse_mode="Markdown",
                     reply_markup=markup)
    return
  if float(amount) > float(bal):
    bot.send_message(user_id,
                     "❌ You can't purchase more views than your balance",
                     parse_mode="Markdown",
                     reply_markup=markup)
    return

  bot.reply_to(message, "enter link now")
  bot.register_next_step_handler(message, view_link, amount)


def is_valid_link(link):
  pattern = r'^https?://t\.me/[a-zA-Z0-9_]{5,}/\d+$'
  return re.match(pattern, link) is not None


def send_order_to_smm_panel(link, amount):
  """ Send the order to the SMM panel and return the result """
  try:
    response = requests.post(url="https://easysmmpanel.com/api/v2",
                             data={
                                 'key': SmmPanelApi,
                                 'action': 'add',
                                 'service': '4815',
                                 'link': link,
                                 'quantity': amount
                             })
    return response.json()
  except requests.RequestException as e:
    print(f"An error occurred while sending order to SMM panel: {e}")
    return None


def view_link(message, amount):
  user_id = message.from_user.id
  link = message.text
  if message.text == "✘ Cancel":
    bot.reply_to(message,
                 "Operation successfully canceled.",
                 reply_markup=markup)
    return
  # Replace this with your actual validation for a Telegram post link
  if not is_valid_link(link):
    bot.send_message(
        user_id,
        "❌ Invalid link provided. Please provide a valid Telegram post link.",
        parse_mode="Markdown",
        reply_markup=markup)
    return

  # Call the SMM panel API
  try:
    result = send_order_to_smm_panel(link, amount)
  except:
    bot.send_message(user_id,
                     "*🤔 Something went wrong please try again later!*",
                     parse_mode="markdown",
                     reply_markup=markup)
    return

  if result is None or 'order' not in result or result['order'] is None:
    bot.send_message(user_id,
                     "*🤔 Something went wrong please try again later!*",
                     parse_mode="markdown",
                     reply_markup=markup)
    if 'error' in result:
      bot.send_message(user_id, result['error'])
    return

  oid = result['order']
  # Here, you should have your own method to retrieve the user's current balance and save the new balance
  cutBalance(user_id, float(amount))

  # Send confirmation message to the user
  bot.send_message(user_id,
                   (f"*✅ Your Order Has Been Submitted and Processing\n\n"
                    f"Order Details :\n"
                    f"ℹ️ Order ID :* `{oid}`\n"
                    f"*🔗 Link : {link}*\n"
                    f"💰 *Order Price :* `{amount} Coins`\n"
                    f"👀 *Tg Post Views  :* `{amount} Views`\n\n"
                    f"😊 *Thanks for ordering*"),
                   parse_mode="markdown",
                   reply_markup=markup,
                   disable_web_page_preview=True)

  # Send notification to the channel about the new order
  bot.send_message(payment_channel,
                   (f"*✅ New Views Order*\n\n"
                    f"*ℹ️ Order ID =* `{oid}`\n"
                    f"*⚡ Status* = `Processing...`\n"
                    f"*👤 User =* {message.from_user.first_name}\n"
                    f"*🆔️ User ID *= `{user_id}`\n"
                    f"*👀 TG Post Views =* `{amount} Views`\n"
                    f"*💰 Order Price :* `{amount} Coins`\n"
                    f"*🔗 Link = {link}*\n\n"
                    f"*🤖 Bot = @{bot.get_me().username}*"),
                   parse_mode="markdown",
                   disable_web_page_preview=True)


if __name__ == '__main__':
  while True:
    try:
      print("bot is running")
      bot.polling(none_stop=True)
      
    except Exception as e:
      print(f"Bot polling failed: {e}")
      # Optionally send a message to the admin about the exception.
      bot.send_message(admin_user_id, f"Bot polling failed: {e}")
      time.sleep(10)  # Wait a bit before restarting the bot polling
