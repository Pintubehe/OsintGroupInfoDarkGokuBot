import os
import json
import logging
import time
import requests
import telebot
from telebot import types
import html

# --------------------------------------------------------------------------------
# CONFIGURATION - RENDER के लिए ठीक किया गया
# --------------------------------------------------------------------------------
# BOT_TOKEN को environment variable से लोड करें (सुरक्षित)
BOT_TOKEN = os.environ.get('8509013592:AAFW1MaBFHd7usJ9NHYb6yWE6fhsZyHhVRY', '')
CHANNEL_USERNAME = '@Gokuuuu00'
CHANNEL_LINK = 'https://t.me/Gokuuuu00'
CHANNEL_ID = -1003144724351
BOT_USERNAME = 'Osint_gokuuuuu_bot'
GOKU_API_KEY = 'GOKU'

# अगर BOT_TOKEN सेट नहीं है, तो error दिखाएं
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable not set!")
    print("ℹ️  Render पर 'Environment' टैब में BOT_TOKEN जोड़ें")
    exit(1)

# Bot initialize करें
bot = telebot.TeleBot(BOT_TOKEN)

# Logging - Render के लिए ठीक किया गया
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# --------------------------------------------------------------------------------
# HELPER FUNCTIONS - आपके original functions
# --------------------------------------------------------------------------------

def get_buttons():
    perms = "change_info+delete_messages+restrict_members+invite_users+pin_messages+manage_video_chats+promote_members"
    add_group_url = f"https://t.me/{BOT_USERNAME}?startgroup=true&admin={perms}"
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton('📢 Join Channel', url=CHANNEL_LINK),
        types.InlineKeyboardButton('➕ Add Me To Your Group', url=add_group_url)
    )
    markup.row(
        types.InlineKeyboardButton('✅ I Have Joined', callback_data='check_join')
    )
    return markup

def check_channel_membership(user_id):
    try:
        try:
            member = bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                return True
        except Exception as e:
            logging.warning(f"Chat ID check failed: {e}")
        
        try:
            chat = bot.get_chat(CHANNEL_USERNAME)
            member = bot.get_chat_member(chat.id, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                return True
        except Exception as e:
            logging.warning(f"Username check failed: {e}")
        
        return False
    except Exception as e:
        logging.error(f"Channel check error: {e}")
        return False

def check_channel_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Channel join check error: {e}")
        return False

@bot.callback_query_handler(func=lambda call: call.data == 'check_join')
def handle_check_join(call):
    user_id = call.from_user.id
    
    if check_channel_join(user_id):
        bot.answer_callback_query(call.id, "✅ सफल! अब आप OSINT commands use कर सकते हैं।", show_alert=True)
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        bot.send_message(
            call.message.chat.id,
            f"""✅ <b>VERIFICATION SUCCESSFUL!</b>

🎉 <b>अब आप सभी OSINT commands use कर सकते हैं!</b>

<b>Available Commands:</b>
<code>/numinfo 9876543210</code> - Number Information
<code>/vehicle MH12AB3456</code> - Vehicle Details
<code>/pan AXDPR2606K</code> - PAN Card Info
<code>/ip 117.237.10.49</code> - IP Address Lookup
<code>/ifsc SBIN0001234</code> - IFSC Code Details
<code>/pin 110001</code> - Pincode Information

<code>/list</code> - सभी commands देखें

<b>Important:</b> ये commands सिर्फ groups में काम करेंगे!""",
            parse_mode='HTML',
            reply_markup=get_buttons()
        )
    else:
        bot.answer_callback_query(
            call.id, 
            f"""❌ अभी तक चैनल जॉइन नहीं किया!

कृपया पहले चैनल जॉइन करें:
{CHANNEL_USERNAME}

जॉइन करने के बाद फिर से 'I Have Joined' बटन दबाएं।""", 
            show_alert=True
        )
        
        bot.send_message(
            call.message.chat.id,
            f"""🚫 <b>CHANNEL JOIN REQUIRED</b>

आप अभी तक चैनल में नहीं हैं!
कृपया पहले चैनल जॉइन करें: {CHANNEL_USERNAME}

✅ जॉइन करने के बाद फिर से "I Have Joined" बटन दबाएं।""",
            parse_mode='HTML',
            reply_markup=get_buttons()
        )

def fetch_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)
        return {'data': response.text, 'code': response.status_code}
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return {'data': None, 'code': 500, 'error': str(e)}

def fetch_and_reply(message, url, target, title, remove_texts=None):
    if remove_texts is None:
        remove_texts = []
    
    try:
        status_msg = bot.reply_to(
            message,
            f"🔄 <b>Fetching {title}...</b>\nTarget: <code>{html.escape(target)}</code>",
            parse_mode='HTML'
        )
        
        res = fetch_url(url)
        
        if res['code'] == 200:
            try:
                data = json.loads(res['data'])
            except json.JSONDecodeError:
                try:
                    import re
                    json_match = re.search(r'\{.*\}', res['data'], re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                    else:
                        data = {"response": res['data'], "note": "Raw Text Response"}
                except:
                    data = {"raw_response": res['data'][:500] + "..." if len(res['data']) > 500 else res['data']}
        else:
            data = {"error": f"API Error - Status {res['code']}", "status": res['code']}
        
        formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
        
        for word in remove_texts:
            formatted_json = formatted_json.replace(word, "")
        
        if len(formatted_json) > 4000:
            formatted_json = formatted_json[:4000] + "\n... [Truncated]"
        
        result_text = f"""<b>{title} ☠️</b>
Target: <code>{html.escape(target)}</code>

<b>JSON RESPONSE:</b>
<pre language='json'>{html.escape(formatted_json)}</pre>

<b>Bot Developer:</b> @gokuuuu_1
<b>Channel:</b> {CHANNEL_USERNAME}"""
        
        bot.edit_message_text(
            chat_id=status_msg.chat.id,
            message_id=status_msg.message_id,
            text=result_text,
            parse_mode='HTML',
            reply_markup=get_buttons()
        )
        
    except Exception as e:
        logging.error(f"Error in fetch_and_reply: {e}")
        try:
            bot.edit_message_text(
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
                text=f"❌ Error fetching data: {str(e)}",
                parse_mode='HTML'
            )
        except:
            pass

# --------------------------------------------------------------------------------
# START COMMAND
# --------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    
    if check_channel_join(user_id):
        if message.chat.type == 'private':
            bot.reply_to(
                message,
                f"""✅ <b>WELCOME TO GOKU OSINT BOT</b>

आप पहले ही चैनल के मेंबर हैं!

<b>Next Steps:</b>
1. बॉट को अपने group में add करें
2. Group में commands use करें

<b>Available Commands in Groups:</b>
<code>/numinfo 9876543210</code> - Number Information
<code>/vehicle MH12AB3456</code> - Vehicle Details
<code>/pan AXDPR2606K</code> - PAN Card Info

<code>/list</code> - सभी commands देखें

<b>Bot Developer:</b> @gokuuuu_1
<b>Channel:</b> {CHANNEL_USERNAME}""",
                parse_mode='HTML',
                reply_markup=get_buttons()
            )
        else:
            bot.reply_to(
                message,
                f"""✅ <b>GOKU OSINT BOT - READY</b>

आप चैनल के मेंबर हैं!
अब आप सभी OSINT commands use कर सकते हैं।

<code>/list</code> - सभी commands देखें

<b>Bot Developer:</b> @gokuuuu_1
<b>Channel:</b> {CHANNEL_USERNAME}""",
                parse_mode='HTML',
                reply_markup=get_buttons()
            )
    else:
        bot.reply_to(
            message,
            f"""🚫 <b>CHANNEL JOIN REQUIRED</b>

❌ आप मेरे चैनल के मेंबर नहीं हैं!

<b>Steps to Use Bot:</b>
1. पहले चैनल जॉइन करें: {CHANNEL_USERNAME}
2. फिर "I Have Joined" बटन दबाएं
3. बॉट को group में add करें
4. तभी commands use कर सकते हैं

<b>Note:</b> ये bot सिर्फ <b>Groups</b> में काम करता है।""",
            parse_mode='HTML',
            reply_markup=get_buttons()
        )

# --------------------------------------------------------------------------------
# COMMAND HANDLERS
# --------------------------------------------------------------------------------

def check_before_command(message):
    if not check_channel_join(message.from_user.id):
        bot.reply_to(
            message,
            f"""🚫 <b>CHANNEL JOIN REQUIRED</b>

कृपया पहले चैनल जॉइन करें: {CHANNEL_USERNAME}

✅ जॉइन करने के बाद "I Have Joined" बटन दबाएं।
तभी आप OSINT commands use कर सकते हैं।""",
            parse_mode='HTML',
            reply_markup=get_buttons()
        )
        return False
    return True

@bot.message_handler(commands=['list', 'lookup', 'help', 'commands'])
def handle_list(message):
    if not check_before_command(message):
        return
    
    commands_text = """<b>GOKU OSINT BOT - COMMAND LIST</b>

<b>Usage Examples:</b>

<code>/numinfo 9876543210</code> - Number Information
<code>/vehicle MH12AB3456</code> - Vehicle Details
<code>/pan AXDPR2606K</code> - PAN Card Info
<code>/ip 117.237.10.49</code> - IP Address Lookup
<code>/ifsc SBIN0001234</code> - IFSC Code Details
<code>/pin 110001</code> - Pincode Information
<code>/pk 923001234567</code> - Pakistan Database
<code>/insta ix7neha</code> - Instagram Info
<code>/bin 448590</code> - BIN Information
<code>/adhar 707465571282</code> - Aadhar Information
<code>/cnic 15601-6938749-3</code> - CNIC Pakistan
<code>/imei 353010111111110</code> - IMEI Info

<b>Note:</b> सिर्फ groups में काम करता है!
<b>Channel:</b> @Gokuuuu00 (Required)
<b>Bot Developer:</b> @gokuuuu_1"""
    
    bot.reply_to(
        message,
        commands_text,
        parse_mode='HTML',
        reply_markup=get_buttons()
    )

# --------------------------------------------------------------------------------
# ALL OSINT COMMANDS
# --------------------------------------------------------------------------------

@bot.message_handler(commands=['numinfo'])
def handle_numinfo(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing Number!</b>\nExample: <code>/numinfo 9876543210</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://num-to-email-all-info-api.vercel.app/?mobile={target}&key=GOKU"
        fetch_and_reply(message, url, target, "NUMBER INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /numinfo: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['vehicle', 'veh'])
def handle_vehicle(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing Vehicle Number!</b>\nExample: <code>/vehicle MH12AB3456</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://vehicle-darkgoku-api-nmhg.vercel.app//vehicle_info?vehicle_no={target}"
        fetch_and_reply(message, url, target, "VEHICLE INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /vehicle: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['pan'])
def handle_pan(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing PAN Number!</b>\nExample: <code>/pan AXDPR2606K</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://pan-info-goku-api-2no2.vercel.app/?pan={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "PAN CARD INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /pan: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['ip'])
def handle_ip(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing IP Address!</b>\nExample: <code>/ip 117.237.10.49</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://ip-info-goku-api.vercel.app/?ip={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "IP ADDRESS LOOKUP")
        
    except Exception as e:
        logging.error(f"Error in /ip: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['ifsc'])
def handle_ifsc(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing IFSC Code!</b>\nExample: <code>/ifsc SBIN0001234</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://ifsc-info-goku-api.vercel.app/?ifsc={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "IFSC CODE DETAILS")
        
    except Exception as e:
        logging.error(f"Error in /ifsc: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['pin'])
def handle_pin(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing Pincode!</b>\nExample: <code>/pin 110001</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://pincode-info-goku-api.vercel.app/?pincode={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "PINCODE INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /pin: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['pk'])
def handle_pk(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing Pakistan Number!</b>\nExample: <code>/pk 923001234567</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://pakistan-info-api-five.vercel.app/api/seller/?mobile={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "PAKISTAN DATABASE")
        
    except Exception as e:
        logging.error(f"Error in /pk: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['insta', 'ig'])
def handle_insta(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing Instagram Username!</b>\nExample: <code>/insta ix7neha</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://insta-info-goku-api.vercel.app/?username={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "INSTAGRAM INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /insta: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['bin'])
def handle_bin(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing BIN Number!</b>\nExample: <code>/bin 448590</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://bin-info-goku-api-uj9b.vercel.app/?bin={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "BIN INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /bin: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['adhar', 'family', 'fam', 'familyinfo'])
def handle_adhar(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing Aadhar Number!</b>\nExample: <code>/adhar 707465571282</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://aadhar-info-goku-api.vercel.app/?aadhar={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "AADHAAR INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /adhar: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['cnic'])
def handle_cnic(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing CNIC Number!</b>\nExample: <code>/cnic 15601-6938749-3</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://cnic-info-goku-api-1211.vercel.app/?cnic={target}&key={GOKU_API_KEY}"
        fetch_and_reply(message, url, target, "CNIC INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /cnic: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['imei'])
def handle_imei(message):
    if not check_before_command(message):
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ <b>Missing IMEI Number!</b>\nExample: <code>/imei 353010111111110</code>", parse_mode='HTML')
            return
        
        target = args[1]
        url = f"https://ng-imei-info.vercel.app/?imei_num={target}"
        fetch_and_reply(message, url, target, "IMEI INFORMATION")
        
    except Exception as e:
        logging.error(f"Error in /imei: {e}")
        bot.reply_to(message, f"❌ Error: {str(e)}", parse_mode='HTML')

# --------------------------------------------------------------------------------
# MAIN EXECUTION - RENDER के लिए ठीक किया गया
# --------------------------------------------------------------------------------

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    ║      GOKU OSINT BOT - RENDER VERSION  ║
    ║      Mode: Polling                    ║
    ║      Bot: @Osint_gokuuuuu_bot         ║
    ║      Developer: @gokuuuu_1            ║
    ║      Channel: @Gokuuuu00 (Required)   ║
    ╚═══════════════════════════════════════╝
    """)
    
    print("✅ Bot initialized successfully")
    print(f"✅ Bot Username: {BOT_USERNAME}")
    print(f"✅ Channel: {CHANNEL_USERNAME}")
    print(f"✅ Python Version: {sys.version.split()[0]}")
    print("\n🔄 Starting bot on Render...")
    
    retry_count = 0
    max_retries = 10
    
    while retry_count < max_retries:
        try:
            print(f"\n🔄 Attempt {retry_count + 1}/{max_retries}")
            print("Bot is now running and listening for commands...")
            print("Press Ctrl+C to stop")
            
            bot.polling(none_stop=True, interval=2, timeout=30)
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Bot stopped by user!")
            break
        except Exception as e:
            retry_count += 1
            logging.error(f"Bot error: {e}")
            if retry_count < max_retries:
                wait_time = 15
                print(f"\n❌ Error occurred. Restarting in {wait_time} seconds... ({retry_count}/{max_retries})")
                time.sleep(wait_time)
            else:
                print("❌ Max retries reached. Bot stopped.")
                break
