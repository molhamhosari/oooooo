import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

app = Flask(__name__)

# إعداد مفتاح API الخاص بـ OpenAI من متغير البيئة
openai.api_key = os.getenv("OPENAI_API_KEY")

# قاموس للأسئلة والأجوبة من النص المقدم
faq = {
    "ما هو التحليل المالي؟": "التحليل المالي هو عملية تقييم الأنشطة المالية للشركة من خلال استخدام البيانات المالية.",
    "ما هي أدوات التحليل المالي؟": "أدوات التحليل المالي تشمل النسب المالية، التحليل الأفقي والرأسي، والتحليل بواسطة التدفقات النقدية.",
    "ما هي النسبة الحالية؟": "النسبة الحالية هي نسبة السيولة الحالية إلى الالتزامات الجارية، وتستخدم لتقييم قدرة الشركة على سداد ديونها القصيرة الأجل.",
    # أضف المزيد من الأسئلة والإجابات هنا...
}

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming messages with a friendly SMS."""
    incoming_msg = request.form.get('Body').strip()
    app.logger.debug(f"Received message: {incoming_msg}")  # لطباعة الرسالة المستلمة للتحقق

    response = MessagingResponse()
    msg = response.message()

    # البحث عن الإجابة في القاموس
    if incoming_msg in faq:
        answer = faq[incoming_msg]
    else:
        # إذا لم يكن السؤال في القاموس، اتصل بـ OpenAI API للحصول على رد ذكي
        answer = get_openai_response(incoming_msg)
    
    msg.body(answer)
    app.logger.debug(f"Sending response: {answer}")  # لطباعة الرد للتحقق

    return str(response)

def get_openai_response(message):
    try:
        # إعداد طلب OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=message,
            max_tokens=150
        )
        # استخراج النص من الرد
        return response.choices[0].text.strip()
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return "عذرًا، لا أستطيع معالجة طلبك حاليًا. يرجى المحاولة لاحقًا."

if __name__ == "__main__":
    app.run(debug=True)
