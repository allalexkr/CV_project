import streamlit as st
from openai import OpenAI
from parse_hh import get_html, extract_vacancy_data, extract_resume_data

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
Проскорь кандидата по степени соответствия вакансии.

Сначала составь краткий аналитический комментарий, объясняющий твою оценку.
Оцени качество резюме по шкале от 1 до 10. Обрати внимание на следующее:
- Понятно ли, с какими задачами и проблемами сталкивался кандидат?
- Описано ли, как именно он их решал?
- Указаны ли результаты и достижения?
- Насколько тщательно оформлено резюме и видно ли, что кандидат умеет анализировать своё влияние на компанию?

Затем представь итоговую оценку соответствия кандидата — по шкале от 1 до 10 в виде:
- Качество резюме
- Соответствие вакансии
- Итоговая оценка
Итоговая оценка должна основываться в том числе на качестве резюме.
""".strip()

def request_gpt(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},  
            {"role": "user", "content": user_prompt},     
        ],
        max_tokens=1000,
        temperature=0,
    )
    return response.choices[0].message.content

# UI
st.title('CV Scoring App')

job_description = st.text_area('Введите ссылку на вакансию')
cv = st.text_area('Введите ссылку на резюме')

if st.button("Проанализировать соответствие"):
    with st.spinner("Парсим данные и отправляем в GPT..."):
        try:
            job_html = get_html(job_description).text
            resume_html = get_html(cv).text

            job_text = extract_vacancy_data(job_html)
            resume_text = extract_resume_data(resume_html)

            prompt = f"# ВАКАНСИЯ\n{job_text}\n\n# РЕЗЮМЕ\n{resume_text}"
            response = request_gpt(SYSTEM_PROMPT, prompt)

            st.subheader("📊 Результат анализа:")
            st.markdown(response)

        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
