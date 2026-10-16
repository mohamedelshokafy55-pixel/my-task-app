import json
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# إعدادات صفحة الويب
st.set_page_config(page_title="نظام إدارة المهام الذكي", page_icon="📝", layout="centered")

# --- كلاسات المهام والحفظ ---
class Task:
    def __init__(self, title, category="عام"):
        self.title = title
        self.category = category
        self.completed = False

    def to_dict(self):
        return {
            "title": self.title,
            "category": self.category,
            "completed": self.completed
        }

class TaskManager:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = []
        self.load_tasks()

    def add_task(self, title, category):
        if not title.strip():
            return False
        new_task = Task(title, category)
        self.tasks.append(new_task)
        self.save_tasks()
        return True

    def save_tasks(self):
        data = [task.to_dict() for task in self.tasks]
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_tasks(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = []
                    for item in data:
                        t = Task(item["title"], item["category"])
                        t.completed = item["completed"]
                        self.tasks.append(t)
            except:
                pass

# تهيئة مدير المهام
manager = TaskManager()

# --- واجهة موقع الويب (Streamlit) ---
st.title("📝 نظام إدارة المهام الذكي")
st.markdown("مرحباً بك في تطبيقك المصنوع بـ **Python & Streamlit**!")

# جلب الطقس وعرضه في الشريط الجانبي (Sidebar)
with st.sidebar:
    st.header("🌤️ حالة الطقس")
    city = st.text_input("اسم المدينة", "Cairo")
    try:
        url = f"https://wttr.in/{city}?format=3&lang=ar"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            st.success(res.text.strip())
        else:
            st.warning("تعذر جلب الطقس.")
    except:
        st.error("مشكلة في الاتصال بالإنترنت.")
    
    st.markdown("---")
    st.info("💡 هذا التطبيق يعمل كـ موقع ويب محلي على جهازك.")

# 1. قسم إضافة مهمة جديدة
st.subheader("➕ إضافة مهمة جديدة")
with st.form("task_form", clear_on_submit=True):
    task_title = st.text_input("عنوان المهمة")
    task_cat = st.text_input("التصنيف (عمل، دراسة، شخصي...)", "عام")
    submit_btn = st.form_submit_button("إضافة المهمة")

    if submit_btn:
        if task_title:
            manager.add_task(task_title, task_cat)
            st.success(f"تم إضافة المهمة: {task_title}")
            st.rerun()
        else:
            st.warning("من فضلك اكتب عنوان المهمة.")

st.markdown("---")

# 2. عرض المهام وإدارتها
st.subheader("📋 قائمة المهام الحالية")
if not manager.tasks:
    st.info("لا توجد مهام حالياً. أضف مهمة جديدة من الأعلى!")
else:
    for index, task in enumerate(manager.tasks):
        col1, col2, col3 = st.columns([0.6, 0.3, 0.1])
        
        with col1:
            status_icon = "✅" if task.completed else "⏳"
            st.markdown(f"**{index+1}. {status_icon} [{task.category}]** {task.title}")
            
        with col2:
            if not task.completed:
                if st.button("إنجاز", key=f"comp_{index}"):
                    task.completed = True
                    manager.save_tasks()
                    st.rerun()
            else:
                if st.button("إلغاء الإنجاز", key=f"uncomp_{index}"):
                    task.completed = False
                    manager.save_tasks()
                    st.rerun()
                    
        with col3:
            if st.button("🗑️", key=f"del_{index}"):
                manager.tasks.pop(index)
                manager.save_tasks()
                st.rerun()

st.markdown("---")

# 3. إحصائيات ورسوم بيانية (Pandas & Matplotlib)
st.subheader("📊 إحصائيات ورسوم بيانية")
if manager.tasks:
    data = [{"الحالة": "مخلص" if t.completed else "قيد الانتظار"} for t in manager.tasks]
    df = pd.DataFrame(data)
    
    status_counts = df['الحالة'].value_counts()
    
    fig, ax = plt.subplots(figsize=(4, 4))
    status_counts.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], ax=ax)
    ax.set_ylabel('')
    ax.set_title('نسبة إنجاز المهام')
    
    st.pyplot(fig)
else:
    st.write("أضف مهام لتعرض الإحصائيات هنا.")