import streamlit as st
import pandas as pd
import io

# পেজ কনফিগারেশন
st.set_page_config(page_title="Maruf Rent Generator", page_icon="🏠", layout="centered")

# ==================== শেয়ারড ফাংশনসমূহ ====================
def to_bangla_formatted(num, is_unit=False):
    if num is None:
        return ""
    if isinstance(num, (int, float)):
        if is_unit:
            formatted_num = "{:,g}".format(num) 
        else:
            formatted_num = "{:,}".format(int(num))
    else:
        formatted_num = str(num).lower()

    eng_to_bng = {'0':'০', '1':'১', '2':'২', '3':'৩', '4':'৪', '5':'৫', '6':'৬', '7':'৭', '8':'৮', '9':'৯', ',':',', '.':'.'}
    eng_to_bng_char = {'a':'এ', 'b':'বি', 'c':'সি', 'd':'ডি', 'e':'ই', 'f':'এফ'}
    
    return "".join(eng_to_bng.get(char, eng_to_bng_char.get(char, char)) for char in formatted_num)

def month_to_bangla(month_text):
    months = {
        'january': 'জানুয়ারি', 'february': 'ফেব্রুয়ারি', 'march': 'মার্চ', 'april': 'এপ্রিল',
        'may': 'মে', 'june': 'জুন', 'july': 'জুলাই', 'august': 'আগস্ট',
        'september': 'সেপ্টেম্বর', 'october': 'অক্টোবর', 'november': 'নভেম্বর', 'december': 'ডিসেম্বর'
    }
    month_clean = str(month_text).strip().lower()
    for eng, ban in months.items():
        if eng in month_clean:
            year = "".join([c for c in month_clean if c.isdigit()])
            if year:
                return f"{ban} {to_bangla_formatted(year)}"
            return ban
    return to_bangla_formatted(month_text)

def custom_round(num):
    return int(num) + 1 if num - int(num) >= 0.5 else int(num)

# সংখ্যা থেকে বাংলায় কথায় লেখার ফাংশন (১ থেকে ৯৯,৯৯৯ পর্যন্ত পারফেক্ট কাজ করবে)
def number_to_bangla_words(n):
    if n <= 0:
        return "শূন্য"
    
    words = {
        0: '', 1: 'এক', 2: 'দুই', 3: 'তিন', 4: 'চার', 5: 'পাঁচ', 6: 'ছয়', 7: 'সাত', 8: 'আট', 9: 'নয়', 10: 'দশ',
        11: 'এগারো', 12: 'বারো', 13: 'তেরো', 14: 'চৌদ্দ', 15: 'পনেরো', 16: 'ষোলো', 17: 'সতেরো', 18: 'আঠারো', 19: 'উনিশ', 20: 'বিশ',
        21: 'একুশ', 22: 'বাইশ', 23: 'তেইশ', 24: 'চব্বিশ', 25: 'পঁচিশ', 26: 'ছাব্বিশ', 27: 'সাতাশ', 28: 'আটাশ', 29: 'উনত্রিশ', 30: 'ত্রিশ',
        31: 'একত্রিশ', 32: 'বত্রিশ', 33: 'তেত্রিশ', 34: 'চৌত্রিশ', 35: 'পঁয়ত্রিশ', 36: 'ছত্রিশ', 37: 'সাতত্রিশ', 38: 'আটত্রিশ', 39: 'ঊনচল্লিশ', 40: 'চল্লিশ',
        41: 'একচল্লিশ', 42: 'বিয়াল্লিশ', 43: 'তেতাল্লিশ', 44: 'চৌয়াল্লিশ', 45: 'পঁয়তাল্লিশ', 46: 'ছেচল্লিশ', 47: 'সাতচল্লিশ', 48: 'আটচল্লিশ', 49: 'ঊনপঞ্চাশ', 50: 'পঞ্চাশ',
        51: 'একান্ন', 52: 'বায়ান্ন', 53: 'তিপ্পান্ন', 54: 'চৌয়ান্ন', 55: 'পঞ্চান্ন', 56: 'ছাপ্পান্ন', 57: 'সাতান্ন', 58: 'আটান্ন', 59: 'ঊনষাট', 60: 'ষাট',
        61: 'একষট্টি', 62: 'বাষট্টি', 63: 'তেষট্টি', 64: 'চৌষট্টি', 65: 'পঁয়ষট্টি', 66: 'ছেষট্টি', 67: 'সাতষট্টি', 68: 'আটষট্টি', 69: 'ঊনসত্তর', 70: 'সত্তর',
        71: 'একাত্তর', 72: 'বাহাত্তর', 73: 'তেয়াত্তর', 74: 'চৌয়াত্তর', 75: 'পঁচাত্তর', 76: 'ছিয়াত্তর', 77: 'সাতাত্তর', 78: 'আটাত্তর', 79: 'ঊনআশি', 80: 'আশি',
        81: 'একাশি', 82: 'বিরাশি', 83: 'তিরাশি', 84: 'চৌরাশি', 85: 'পঁচাশি', 86: 'ছিয়াশি', 87: 'সাতাশি', 88: 'আটাশি', 89: 'ঊননব্বই', 90: 'নব্বই',
        91: 'একানব্বই', 92: 'বিরানব্বই', 93: 'তিরানব্বই', 94: 'চৌরানব্বই', 95: 'পঁচানব্বই', 96: 'ছিয়ানব্বই', 97: 'সাতানব্বই', 98: 'আটানব্বই', 99: 'নিরানব্বই'
    }
    
    res = ""
    # হাজার হ্যান্ডেল করার জন্য
    if n >= 1000:
        thousand = n // 1000
        res += words[thousand] + " হাজার "
        n %= 1000
    # শতক হ্যান্ডেল করার জন্য
    if n >= 100:
        hundred = n // 100
        res += words[hundred] + " শত "
        n %= 100
    # দশক ও একক হ্যান্ডেল করার জন্য
    if n > 0:
        res += words[n]
        
    return res.strip() + " টাকা মাত্র।"


# ==================== সাইডবার মেনু নেভিগেশন ====================
st.sidebar.title("📱 মেনু নির্বাচন করুন")
app_mode = st.sidebar.radio(
    "কোনটি তৈরি করতে চান?",
    ["📋 বাড়ি ভাড়ার বিবরণ (Bill Notice)", "💵 ভাড়ার রসিদ (Cash Memo)"]
)

st.sidebar.write("---")
st.sidebar.caption("💁‍♂️ ডেভেলপার: মারুফ")


# ==================== মোড ১: বাড়ি ভাড়ার বিবরণ (Bill Notice) ====================
if app_mode == "📋 বাড়ি ভাড়ার বিবরণ (Bill Notice)":
    st.title("🏠 বিস্তারিত বাড়ি ভাড়ার বিবরণ জেনারেটর")
    st.write("বিদ্যুৎ বিল, পানির বিলসহ মাসের শুরুতে ভাড়াটিয়াকে পাঠানোর নোটিশ।")
    
    tab1, tab2 = st.tabs(["সিঙ্গেল ইনপুট (Manual)", "এক্সেল আপলোড (Bulk)"])
    
    def generate_receipt_text(flat_no, month_year, rent_amount, unit_consumed, per_unit_cost, water_bill, cleaning_bill, arrears, advance):
        try:
            rent = int(rent_amount)
            unit = float(unit_consumed)
            rate = float(per_unit_cost)
            water = int(water_bill)
            cleaning = int(cleaning_bill)
            arr = int(arrears)
            adv = int(advance)
            
            electricity_total = custom_round(unit * rate)
            total_final = custom_round((rent + (unit * rate) + water + cleaning + arr) - adv)
            
            flat_bn = to_bangla_formatted(flat_no).upper()
            month_bn = month_to_bangla(month_year)
            in_words_bn = number_to_bangla_words(total_final)
            
            # বকেয়া থাকার ওপর ভিত্তি করে ডাইনামিক রিমাইন্ডার মেসেজ
            if arr > 0:
                reminder_msg = f"⚠️ বকেয়া নোটিশ: আপনার পূর্বের {to_bangla_formatted(arr)}৳ বকেয়াসহ চলতি মাসের বিলটি দ্রুত পরিশোধ করার জন্য অনুরোধ করা হলো।"
            else:
                reminder_msg = "📌 👉 নির্ধারিত সময়ের মধ্যে বিলটি পরিশোধ করার জন্য বিনীত অনুরোধ রইল।"
            
            return f"""🌟✨ ━━《 🏠 বাড়ি ভাড়ার বিবরণ 🏠 》━━ ✨🌟
🏡 ফ্ল্যাট: {flat_bn}

📅 মাস: {month_bn}
📋 বিস্তারিত হিসাব:
━━━━━━━━━━━━━━━━━━━
🏠 বাড়ি ভাড়া: {to_bangla_formatted(rent)}৳
⚡ বৈদ্যুতিক বিল: {to_bangla_formatted(unit, is_unit=True)}×{to_bangla_formatted(rate)} = {to_bangla_formatted(electricity_total)}৳
🚿 পানির বিল: {to_bangla_formatted(water)}৳
🧹🗑 ক্লিনিং ও আবর্জনা বিল: {to_bangla_formatted(cleaning)}৳
📌 পূর্বের বকেয়া: {to_bangla_formatted(arr)}৳
💰 অগ্রিম জমা: -{to_bangla_formatted(adv)}৳
━━━━━━━━━━━━━━━━━━━
💵 মোট পরিশোধযোগ্য: ({to_bangla_formatted(rent)}+{to_bangla_formatted(electricity_total)}+{to_bangla_formatted(water)}+{to_bangla_formatted(cleaning)}+{to_bangla_formatted(arr)}-{to_bangla_formatted(adv)})
🎯 সর্বমোট: {to_bangla_formatted(total_final)}✅
✍️ কথায়: {in_words_bn}

{reminder_msg}

🌟 শুভেচ্ছান্তে,
💁‍♂️ মারুফ"""
        except Exception as e:
            return f"ভুল ইনপুট! ডাটা চেক করুন। এরর: {e}"

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            flat = st.text_input("ফ্ল্যাট নম্বর", value="1A", key="notice_flat")
            month = st.text_input("মাস ও বছর", value="January 2026", key="notice_month")
            rent = st.number_input("বাড়ি ভাড়া", value=5000, step=100, key="notice_rent")
            unit = st.number_input("বিদ্যুৎ ইউনিট", value=9.0, step=1.0, key="notice_unit")
            rate = st.number_input("প্রতি ইউনিট রেট", value=102.77, step=0.1, key="notice_rate")
            water = st.number_input("পানির বিল", value=100, step=10, key="notice_water")
            cleaning = st.number_input("ক্লিনিং বিল", value=160, step=10, key="notice_clean")
            arrears = st.number_input("বকেয়া (Arrears)", value=930, step=10, key="notice_arr")
            advance = st.number_input("নগদ অগ্রিম জমা", value=0, step=10, key="notice_adv")
            
        with col2:
            st.subheader("📋 আপনার নোটিশ রেডি:")
            notice_msg = generate_receipt_text(flat, month, rent, unit, rate, water, cleaning, arrears, advance)
            st.code(notice_msg, language=None)

    with tab2:
        st.subheader("📂 এক্সেল ফাইল আপলোড করুন (Bulk System)")
        st.caption("এক্সেলের কলামগুলোর নাম হুবহু নিচের মতো হতে হবে:")
        st.code("flat_no, month_year, rent_amount, unit_consumed, per_unit_cost, water_bill, cleaning_bill, arrears, advance", language=None)
        
        uploaded_file = st.file_uploader("আপনার এক্সেল (.xlsx) ফাইলটি নির্বাচন করুন", type="xlsx")
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ সফলভাবে {len(df)} টি বিল প্রসেস করা হয়েছে!")
                all_receipts = ""
                
                for index, row in df.iterrows():
                    receipt = generate_receipt_text(
                        row['flat_no'], row['month_year'], row['rent_amount'], 
                        row['unit_consumed'], row['per_unit_cost'], row['water_bill'], 
                        row['cleaning_bill'], row['arrears'], row['advance']
                    )
                    all_receipts += receipt + "\n\n" + "═"*40 + "\n\n"
                
                st.write("### 📋 সব ফ্ল্যাটের মেসেজ নিচে একসাথে রেডি:")
                st.code(all_receipts, language=None)
            except Exception as e:
                st.error(f"ফাইল প্রসেস করতে সমস্যা হয়েছে। কলামের নামগুলো ঠিক আছে কিনা নিশ্চিত করুন। এরর: {e}")


# ==================== মোড ২: ভাড়ার রסיদ (Cash Memo) ====================
elif app_mode == "💵 ভাড়ার রסיদ (Cash Memo)":
    st.title("🏡 ভাড়ার রসিদ জেনারেটর (টাকা জমার মেমো)")
    st.write("ভাড়াটিয়া টাকা পরিশোধ করার পর বকেয়া/অগ্রিম হিসাবের রসিদ তৈরি করুন।")
    
    col1, col2 = st.columns(2)
    with col1:
        flat_no_raw = st.text_input("📍 ফ্ল্যাট নং (যেমন: 1A বা 2B)", "1A", key="memo_flat")
        month_input = st.selectbox("📅 মাস নির্বাচন করুন", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], key="memo_month")
        year_raw = st.text_input("📆 বছর", "2026", key="memo_year")
    with col2:
        total_bill_raw = st.number_input("🏠 মোট ভাড়া (Total Bill)", min_value=0, value=7115, step=1)
        paid_amount_raw = st.number_input("💵 পরিশোধ করেছেন (Paid)", min_value=0, value=7000, step=1)
        name = st.text_input("💁‍♂️ শুভেচ্ছান্তে", "মারুফ", key="memo_name")

    if st.button("রসিদ তৈরি করুন ✨", type="primary"):
        flat_no_bn = to_bangla_formatted(flat_no_raw).upper()
        year_bn = to_bangla_formatted(year_raw)
        month_bn = month_to_bangla(month_input)
        
        total_bill = int(total_bill_raw)
        paid_amount = int(paid_amount_raw)
        
        current_due = 0
        current_adv = 0
        status_msg = ""
        due_display = "০৳"
        adv_display = "০৳"
        
        if paid_amount < total_bill:
            current_due = total_bill - paid_amount
            status_msg = "✅ আপনার আংশিক ভাড়া গ্রহণ করা হয়েছে।\n🙏 অনুগ্রহ করে দ্রুত বকেয়াটুকু পরিশোধের চেষ্টা করবেন।"
            due_display = f"{to_bangla_formatted(current_due)}৳ ⚠️"
        elif paid_amount > total_bill:
            current_adv = paid_amount - total_bill
            status_msg = "🌸 ধন্যবাদ! আপনার অতিরিক্ত জমা টাকা পরবর্তী\nমাসের ভাড়ার সাথে সমন্বয় করা হবে।"
            adv_display = f"{to_bangla_formatted(current_adv)}৳ ⭐"
        else:
            status_msg = "✨ আলহামদুলিল্লাহ, আপনার এই মাসের ভাড়া\nসম্পূর্ণ পরিশোধ হয়েছে। ধন্যবাদ। 🤝"
            due_display = "০৳ (পরিশোধিত)"

        receipt = f"""╔══🏡✨ ভাড়ার রসিদ ✨🏡══╗
📍 ফ্ল্যাট নং: {flat_no_bn}
📅 মাস: {month_bn} {year_bn}
╠══════════════════════╣
🏠 মোট ভাড়া            : {to_bangla_formatted(total_bill)}৳
💵 পরিশোধ করেছেন      : {to_bangla_formatted(paid_amount)}৳
📌 বকেয়া               : {due_display}
💰 অগ্রিম               : {adv_display}
╠══════════════════════╣
{status_msg}
🌿 আল্লাহ আপনার রিজিকে বরকত দান করুন।
╚════ 💁‍♂️ {name} ════╝"""

        st.write("### 📋 আপনার রসিদ রেডি:")
        st.code(receipt, language=None)
