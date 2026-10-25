"""Hand-written seed templates. Used (a) as fallback when no Sarvam key is set,
and (b) to sanity-test the pipeline offline. Real data comes from gen_data.py."""
import random

T = {
    "hindi": {
        "scam": [
            "आपके नाम से एक पार्सल पकड़ा गया है जिसमें ड्रग्स मिले हैं। आप डिजिटल अरेस्ट में हैं, वीडियो कॉल पर रहें और अभी ₹{amt} जमा करें।",
            "आपका बैंक खाता KYC अपडेट न होने से आज बंद हो जाएगा। इस लिंक पर क्लिक करें http://kyc-{num}.xyz और OTP बताएं।",
            "बधाई हो! आपने KBC लॉटरी में ₹{amt} जीते हैं। इनाम पाने के लिए ₹{fee} प्रोसेसिंग फीस भेजें।",
            "आपका बिजली बिल बकाया है, आज रात 9 बजे कनेक्शन कट जाएगा। तुरंत इस नंबर {num} पर कॉल करें।",
        ],
        "legit": [
            "आपके खाते से ₹{amt} डेबिट हुए। यह आप नहीं थे तो बैंक की शाखा में संपर्क करें।",
            "माँ, मैं शाम को 7 बजे तक घर पहुँच जाऊँगा, खाना मत बनाना।",
            "आपका ऑर्डर कल सुबह 10 बजे तक डिलीवर होगा। ट्रैकिंग ID {num}।",
            "कल की मीटिंग 11 बजे है, कृपया समय पर आएँ।",
        ],
    },
    "hinglish": {
        "scam": [
            "Sir aapka parcel customs me pakda gaya hai, CBI officer se baat karo, abhi Rs {amt} transfer karo warna arrest hoga.",
            "Dear customer aapka SBI account block ho jayega, PAN update karne ke liye link click karo http://sbi-{num}.in",
            "Congratulations! Aapne Rs {amt} ka lucky draw jeeta hai, claim karne ke liye Rs {fee} fee bhejo.",
            "Aapka electricity bill pending hai, aaj raat light kat jayegi, turant {num} par call karo aur UPI PIN bhejo.",
        ],
        "legit": [
            "Bhai kal match dekhne chalega? 8 baje aa jana.",
            "Aapka OTP {num} hai. Isse kisi ko share na karein. - HDFC Bank",
            "Amazon order {num} kal tak deliver ho jayega.",
            "Rent Rs {amt} transfer kar diya hai, check kar lena.",
        ],
    },
    "tamil": {
        "scam": [
            "உங்கள் பெயரில் வந்த பார்சலில் போதைப்பொருள் உள்ளது. நீங்கள் டிஜிட்டல் கைதில் உள்ளீர்கள், உடனே ₹{amt} அனுப்புங்கள்.",
            "உங்கள் வங்கி கணக்கு KYC புதுப்பிக்காததால் இன்று முடக்கப்படும். இந்த லிங்கை கிளிக் செய்து OTP சொல்லுங்கள் http://kyc-{num}.xyz",
            "வாழ்த்துகள்! நீங்கள் ₹{amt} லாட்டரி வென்றுள்ளீர்கள். பரிசைப் பெற ₹{fee} கட்டணம் அனுப்புங்கள்.",
            "உங்கள் மின் கட்டணம் நிலுவையில் உள்ளது, இன்று இரவு மின் இணைப்பு துண்டிக்கப்படும். உடனே {num} எண்ணை அழைக்கவும்.",
        ],
        "legit": [
            "அம்மா, நான் மாலை 7 மணிக்குள் வீடு வந்துவிடுவேன்.",
            "உங்கள் OTP {num}. இதை யாரிடமும் பகிர வேண்டாம்.",
            "உங்கள் ஆர்டர் நாளை காலை 10 மணிக்குள் டெலிவரி செய்யப்படும்.",
            "நாளைய கூட்டம் 11 மணிக்கு, தயவுசெய்து நேரத்திற்கு வரவும்.",
        ],
    },
    "bengali": {
        "scam": [
            "আপনার নামে আসা পার্সেলে মাদক পাওয়া গেছে। আপনি ডিজিটাল অ্যারেস্টে আছেন, এখনই ₹{amt} জমা দিন।",
            "আপনার ব্যাংক অ্যাকাউন্ট KYC আপডেট না হওয়ায় আজ বন্ধ হয়ে যাবে। এই লিঙ্কে ক্লিক করে OTP দিন http://kyc-{num}.xyz",
            "অভিনন্দন! আপনি ₹{amt} লটারি জিতেছেন। পুরস্কার পেতে ₹{fee} ফি পাঠান।",
            "আপনার বিদ্যুৎ বিল বকেয়া, আজ রাতে সংযোগ কেটে দেওয়া হবে। এখনই {num} নম্বরে ফোন করুন।",
        ],
        "legit": [
            "মা, আমি সন্ধ্যা ৭টার মধ্যে বাড়ি পৌঁছে যাব।",
            "আপনার OTP {num}। এটি কারো সাথে শেয়ার করবেন না।",
            "আপনার অর্ডার আগামীকাল সকাল ১০টার মধ্যে ডেলিভারি হবে।",
            "কালকের মিটিং ১১টায়, দয়া করে সময়মতো আসবেন।",
        ],
    },
    "marathi": {
        "scam": [
            "तुमच्या नावाने आलेल्या पार्सलमध्ये ड्रग्ज सापडले आहेत. तुम्ही डिजिटल अरेस्टमध्ये आहात, लगेच ₹{amt} भरा.",
            "तुमचे बँक खाते KYC अपडेट नसल्याने आज बंद होईल. या लिंकवर क्लिक करा आणि OTP सांगा http://kyc-{num}.xyz",
            "अभिनंदन! तुम्ही ₹{amt} ची लॉटरी जिंकली आहे. बक्षीस मिळवण्यासाठी ₹{fee} फी पाठवा.",
            "तुमचे वीज बिल थकीत आहे, आज रात्री कनेक्शन तोडले जाईल. लगेच {num} वर कॉल करा.",
        ],
        "legit": [
            "आई, मी संध्याकाळी ७ पर्यंत घरी पोहोचेन.",
            "तुमचा OTP {num} आहे. कोणालाही सांगू नका.",
            "तुमची ऑर्डर उद्या सकाळी १० पर्यंत पोहोचेल.",
            "उद्याची मीटिंग ११ वाजता आहे, कृपया वेळेवर या.",
        ],
    },
}

PREFIX = ["", "", "", "Urgent: ", "Sir, ", "Alert! ", "Notice: ", "Dear user, "]


def make_seed_data(per_template: int = 8, seed: int = 0):
    rng = random.Random(seed)
    rows = []
    for lang, d in T.items():
        for label_name, templates in d.items():
            label = 1 if label_name == "scam" else 0
            for t in templates:
                for _ in range(per_template):
                    text = t.format(
                        amt=rng.choice([499, 2000, 5000, 9999, 15000, 48000, 120000]),
                        fee=rng.choice([199, 500, 999, 2500]),
                        num=rng.randint(100000, 999999),
                    )
                    rows.append({"text": rng.choice(PREFIX) + text, "label": label, "lang": lang})
    rng.shuffle(rows)
    return rows
