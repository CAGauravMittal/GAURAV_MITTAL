import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import re
from pathlib import Path
from collections import defaultdict

st.set_page_config(
    page_title="CA AI Training - Day 1 Assessment",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

Path("responses").mkdir(exist_ok=True)

st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 15px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 15px;
        border-radius: 8px;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 15px;
        border-radius: 8px;
        color: #721c24;
    }
    .instructor-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    defaults = {
        'page': 'home',
        'responses': {},
        'student_name': "",
        'student_email': "",
        'student_phone': "",
        'instructor_authenticated': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

mcq_data = {
    1: {
        'question': "CA GPT Implementation Challenge\n\nYour firm has subscribed to CA GPT (ICAI's AI platform) with access to 5000+ annual reports. A partner asks you to use it to analyze whether a potential audit client (listed on NSE, software sector) is experiencing revenue recognition issues. What is the MOST APPROPRIATE use of CA GPT for this task?",
        'options': {
            'a': "Upload client's financial statements directly to CA GPT and get instant fraud detection verdict to present to partner",
            'b': "Use CA GPT to extract comparable company data, revenue trends, and accounting policies from industry database; then apply professional judgment to identify potential revenue recognition risks",
            'c': "Use CA GPT to prepare the entire audit risk assessment without further review; trust its analysis",
            'd': "Don't use CA GPT for listed companies; it's only for small/medium firms"
        },
        'correct': 'b',
        'topic': 'CA GPT Usage',
        'difficulty': 'Medium'
    },
    2: {
        'question': "ChatGPT vs Claude for GST Compliance\n\nYour GST compliance team uses both ChatGPT 4o and Claude 3.5 Sonnet for analyzing GSTR-1 vs GSTR-2B mismatches. After testing both on 20 complex mismatches, you found:\n- ChatGPT correctly identifies reason in 85% of cases\n- Claude correctly identifies reason in 92% of cases\n\nHowever, Claude takes 2 minutes longer per analysis. Your team has 500 potential mismatches to review before filing. What is the PRACTICAL recommendation?",
        'options': {
            'a': "Use ChatGPT for all 500 - speed is more important than accuracy",
            'b': "Use Claude for all 500 - accuracy worth the extra time investment",
            'c': "Use Claude for complex/high-value mismatches (>₹5 lakhs); ChatGPT for routine ones (<₹1 lakh)",
            'd': "Hire additional staff instead of using AI - safer option"
        },
        'correct': 'c',
        'topic': 'Tool Comparison',
        'difficulty': 'Hard'
    },
    3: {
        'question': "Prompt Engineering - Expense Audit\n\nYou're auditing a consulting firm's expenses. You want AI to analyze 300 employee expense reports for policy violations. Which prompt would be MOST EFFECTIVE for this scenario?",
        'options': {
            'a': "Check if expenses are valid",
            'b': "You are internal audit partner. Review attached 300 expense reports against this policy - Flight: Only first class for flights >4 hours (max 120000 rupees per ticket) - Hotel: Max 12000 rupees per night, 3-star or below - Meals: 800 rupees per day per diem, or receipt reimbursement - Entertainment: Client entertainment 5000 rupees per person max. Flag: (1) Policy violations (2) Borderline cases (3) Risk indicators. Format: Excel-ready table with columns: Employee, Amount, Policy, Violation Type, Recommended Action, Manager",
            'c': "Analyze expenses and tell me if anything is wrong",
            'd': "Use machine learning to predict which employees will submit fraudulent expenses"
        },
        'correct': 'b',
        'topic': 'Prompt Engineering',
        'difficulty': 'Medium'
    },
    4: {
        'question': "Reinforcement Learning - Tally Integration\n\nYour firm has Tally Prime with ODBC enabled. You want to build a system that learns to automatically flag suspicious journal entries. How would reinforcement learning help in this scenario?",
        'options': {
            'a': "Show the system 100 examples of legitimate journal entries and it will reject all others",
            'b': "The system flags all unusual entries, gets feedback monthly from partner about fraudulent or legitimate items, adjusts thresholds quarterly to improve accuracy",
            'c': "Use past audit findings only without ongoing learning",
            'd': "This is supervised learning, not reinforcement learning"
        },
        'correct': 'b',
        'topic': 'Reinforcement Learning',
        'difficulty': 'Hard'
    },
    5: {
        'question': "Bias in AI - Audit Risk Assessment\n\nAn AI audit tool, trained on 10 years of firm's audit data, consistently flags transactions >20 lakhs from certain vendors as high-risk while flagging transactions >50 lakhs from established vendors as low-risk. What is the PRIMARY concern?",
        'options': {
            'a': "The AI is correctly identifying vendor patterns based on historical data",
            'b': "The AI has learned bias: it underweights materiality for familiar vendors and overweights it for newer vendors - this could miss significant issues",
            'c': "Vendors don't matter; only transaction amount matters",
            'd': "This bias is good for efficiency - focus on new vendors only"
        },
        'correct': 'b',
        'topic': 'AI Bias Detection',
        'difficulty': 'Hard'
    },
    6: {
        'question': "Month-End Close Automation\n\nA CFO of 500 crore revenue manufacturing company has this month-end close process: Tally exports (manual) 20 min, Variance analysis 40 min, Expense accruals 30 min, Manual commenting 30 min. Total 120 min per month. Using Tally ODBC + Power BI + ChatGPT API integration, after 2-day setup, what is REALISTIC outcome by month 2?",
        'options': {
            'a': "120 → 30 min (75% reduction) - still needs quality review and judgment",
            'b': "120 → 10 min (92% reduction) - fully automated, no review needed",
            'c': "No change - too complex to automate without custom coding",
            'd': "120 → 60 min (50% reduction) - modest improvement, not worth setup effort"
        },
        'correct': 'a',
        'topic': 'Automation ROI',
        'difficulty': 'Medium'
    },
    7: {
        'question': "Expense Reconciliation - Compliance Issue\n\nA startup's expense data shows: Employee Rakesh submitted 5 hotel bills from Hotel Paradise at exactly 12000 rupees per night for 20 consecutive days. Policy allows 12000 rupees per night max. All within policy technically. But statistically, staying in same 3-star hotel for 20 days at EXACTLY policy limit is highly unusual. What should an AI auditing tool flag here?",
        'options': {
            'a': "No issue - all within policy limits",
            'b': "SUSPICIOUS PATTERN: Consistent exact-limit compliance across 20 days suggests potential fabrication of expenses. Recommend: (1) Verify hotel receipts and stay dates (2) Check travel project dates (3) Review employee's travel pattern",
            'c': "Approve all 20 days - employee is budget-conscious",
            'd': "Flag only if even ONE day exceeds policy"
        },
        'correct': 'b',
        'topic': 'Anomaly Detection',
        'difficulty': 'Medium'
    },
    8: {
        'question': "AI for Month-End Accruals\n\nA 200 crore IT services company has complex accruals: employee bonuses (variable), warranty provisions (estimated), project revenue adjustments (percentage complete method). CFO currently spends 6 hours monthly calculating these accruals. Using Tally database + ODBC connection to AI (ChatGPT with Excel), what is MOST feasible for automation?",
        'options': {
            'a': "100% automation - AI calculates all accruals without human review",
            'b': "70-80% automation - AI extracts data, calculates, suggests accruals; CFO reviews/approves in 1.5 hours",
            'c': "30% automation - AI helps with data organization only",
            'd': "No automation possible - too complex and judgment-based"
        },
        'correct': 'b',
        'topic': 'Complex Accounting',
        'difficulty': 'Hard'
    },
    9: {
        'question': "Anomaly in Financial Data\n\nAudit of Fintech startup PayQuick Ltd (FY 2024-25): Monthly revenue Oct-Dec 2024: 8cr, 8.5cr, 9cr (steady). January 2025: 22cr (145% jump). Feb-Mar 2025: 9.5cr, 10cr (back to normal). Company claims January was product launch month in new market (Singapore). Management provided: 22cr revenue from 3 Singapore customers. Singapore customer PAN numbers (seems odd for foreign customers). No documentation of market research or product adaptation costs. As auditor using AI for anomaly detection, what is your NEXT step?",
        'options': {
            'a': "Accept explanation - this is normal in fintech startup; approve revenue",
            'b': "Flag for investigation: Large one-time revenue from new market; verify: (1) Customer legitimacy (2) Performance obligations (3) Collection (4) Why no repeat in Feb",
            'c': "Reject revenue - startups cannot have such large deals",
            'd': "This is not an audit issue; focus on other areas"
        },
        'correct': 'b',
        'topic': 'Revenue Anomaly',
        'difficulty': 'Hard'
    },
    10: {
        'question': "GST Compliance Automation\n\nYour firm audits a 150cr distributor with operations in Maharashtra, Gujarat, Tamil Nadu, Delhi. GST compliance check currently takes 40 hours per month. Using Power BI + Tally ODBC + ChatGPT for GST analysis, what is the expected timeline for implementation?",
        'options': {
            'a': "Week 1: Connect Tally ODBC to Power BI; Week 2: Build GST reconciliation dashboard; Week 3: AI prompts. Result: 40 hours → 8-10 hours per month (75% reduction)",
            'b': "Week 1-2: Build automated reconciliation; Week 3: Train team. Result: 40 hours → 15-20 hours per month (60% reduction)",
            'c': "Day 1: Connect; Day 2-7: Testing; Week 2: Go-live. Result: 40 hours → 2-3 hours per month (95% reduction)",
            'd': "Too complex; manual process more reliable"
        },
        'correct': 'a',
        'topic': 'GST Automation',
        'difficulty': 'Hard'
    },
    11: {
        'question': "Transfer Pricing in Digital Economy\n\nYour client CloudServe India (IT services) has this structure: India entity develops software (costs 50 lakhs). US entity (Delaware corp) sells to US customers as SaaS (charges 10000 dollars per month for 50 customers = 40+ crore annual revenue). TP arrangement: India charges US entity 50 lakhs annually for development. Income Tax Department challenges this TP (says underpriced). What should AI-assisted TP analysis focus on?",
        'options': {
            'a': "Accept current TP; no need to adjust",
            'b': "Analyze: (1) What do comparable IT companies charge for similar SaaS development (2) What percentage of US revenue should India entity receive (3) What functions does India entity perform vs US entity (4) Is TP defensible under Indian TP rules",
            'c': "Just increase India's charge to 2 crore to be safe",
            'd': "Do not engage with IT Department; dispute everything"
        },
        'correct': 'b',
        'topic': 'Transfer Pricing',
        'difficulty': 'Hard'
    },
    12: {
        'question': "Going Concern Assessment\n\nManufacturing company SteelTech Ltd audit: Revenue FY24: 200cr; FY25: 180cr (declining). Net loss FY25: 20cr (vs 15cr profit prior year). Bank balance: 5cr (down from 50cr). Debt due in 12 months: 80cr. Current ratio: 0.4. BUT: Management obtained Letter of credit from Development Bank for 60cr to refinance debt. New order from Govt of India for 150cr (contract signed, 2-year delivery). What is the CORRECT audit opinion approach?",
        'options': {
            'a': "Adverse opinion - company clearly insolvent",
            'b': "Unqualified opinion with Emphasis of Matter paragraph stating that going concern depends on loan refinancing and Govt contract execution",
            'c': "Qualified opinion - too much uncertainty",
            'd': "No going concern issue - Govt orders are guaranteed"
        },
        'correct': 'b',
        'topic': 'Going Concern',
        'difficulty': 'Hard'
    },
    13: {
        'question': "Bank Reconciliation - Automation with ODBC\n\nYour firm uses Tally + Power BI ODBC automation for monthly bank reconciliation of 3 bank accounts (company has 500cr+ cash). Automated system flags: 50 lakhs bank transfer from unknown entity dated 30th Sept, marked as investment income but not requested by company. Settlement clearing in bank statement for transaction posted in Tally but dated 3 months ago. What is CORRECT audit action?",
        'options': {
            'a': "Ignore - reconciliation matches; no further testing needed",
            'b': "Investigate BOTH: (1) Is 50 lakh receipt legitimate or fraudulent (2) Why 3-month delay in settlement - could indicate backdated transaction or manipulation",
            'c': "Approve reconciliation - computer says it matches",
            'd': "These are timing differences; routine"
        },
        'correct': 'b',
        'topic': 'Bank Reconciliation',
        'difficulty': 'Hard'
    },
    14: {
        'question': "Data Security Breach Scenario\n\nYou are using ChatGPT to analyze a client's expense dataset for variance analysis. You paste the following: Employees with highest expenses: Rajesh (CEO) 45 lakhs, Priya (CFO) 22 lakhs, Amit (CTO) 18 lakhs. Total 50 employees, total spend 3.5 crores. What is the PROFESSIONAL ERROR here?",
        'options': {
            'a': "None - this is aggregate data",
            'b': "You have identified specific individuals by name, function, and amounts. This is CONFIDENTIAL client information. ChatGPT may use inputs for training. BREACH.",
            'c': "Using ChatGPT for any client analysis is fine; this is normal practice",
            'd': "Only problem if you pasted the ENTIRE report, not summary"
        },
        'correct': 'b',
        'topic': 'Data Security',
        'difficulty': 'Medium'
    },
    15: {
        'question': "AI Hallucination - Tax Scenario\n\nA client asks: Can we claim 100% deduction for consulting fees paid to Group's Singapore entity under Section 37(1)? ChatGPT responds: Yes, Section 37(1) allows 100% deduction for ordinary and necessary business expenses, including consulting fees to related entities. Before advising the client, you verify this against current Income Tax Act. What do you discover?",
        'options': {
            'a': "ChatGPT was correct - 100% deduction allowed",
            'b': "ChatGPT hallucinated: While Section 37(1) allows deduction, it requires: Invoice on proper letterhead with tax ID, Transfer pricing documentation (Section 92), TP study proving arm's length rate",
            'c': "Deduction is denied - cannot pay related parties",
            'd': "This is too complex for AI; do not use AI for tax"
        },
        'correct': 'b',
        'topic': 'AI Hallucination',
        'difficulty': 'Hard'
    }
}

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    return len(name.strip()) >= 3

def save_response(email, responses, student_name, student_phone):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"responses/responses_{email}_{timestamp}.json"
        
        data = {
            'timestamp': timestamp,
            'name': student_name,
            'email': email,
            'phone': student_phone,
            'responses': responses
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename
    except Exception as e:
        st.error(f"Error saving response: {str(e)}")
        return None

def load_all_responses():
    all_data = []
    try:
        if os.path.exists("responses"):
            for filename in os.listdir("responses"):
                if filename.endswith(".json"):
                    filepath = os.path.join("responses", filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_data.append(data)
    except Exception as e:
        st.error(f"Error loading responses: {str(e)}")
    
    return all_data

def calculate_score(responses):
    score = 0
    correct_answers = {}
    
    try:
        for q_num, answer in responses.items():
            q_num = int(q_num)
            if answer == mcq_data[q_num]['correct']:
                score += 1
            correct_answers[q_num] = mcq_data[q_num]['correct']
        
        return score, correct_answers
    except Exception as e:
        st.error(f"Error calculating score: {str(e)}")
        return 0, {}

def home_page():
    st.markdown("""
        <div class="header-container">
            <h1>📋 CA AI Training - Day 1 Assessment</h1>
            <p style='font-size: 18px; margin: 10px 0;'>MCQ Assessment for Chartered Accountants</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Student Mode")
        st.info("📝 Take the assessment and view your score")
        if st.button("▶️ Start Assessment", key="student_btn", use_container_width=True):
            st.session_state.page = 'student_login'
            st.rerun()
    
    with col2:
        st.subheader("👨‍🏫 Instructor Mode")
        st.info("📊 View analytics and student performance")
        if st.button("🔓 Instructor Login", key="instructor_btn", use_container_width=True):
            st.session_state.page = 'instructor_login'
            st.rerun()

def student_login_page():
    st.markdown("""
        <div class="header-container">
            <h1>📋 CA AI Training - Day 1 Assessment</h1>
            <p style='font-size: 18px; margin: 10px 0;'>Student Information</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Enter Your Details")
        
        name = st.text_input("Full Name *", placeholder="Enter your full name")
        email = st.text_input("Email ID *", placeholder="Enter your email")
        phone = st.text_input("Phone Number *", placeholder="Enter 10-digit phone number")
        
        st.write("---")
        
        col_submit, col_back = st.columns([1, 1])
        
        with col_submit:
            if st.button("▶️ Start Assessment", use_container_width=True):
                errors = []
                
                if not validate_name(name):
                    errors.append("Name must be at least 3 characters")
                if not validate_email(email):
                    errors.append("Invalid email format")
                if not validate_phone(phone):
                    errors.append("Phone must be 10 digits")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    st.session_state.student_name = name
                    st.session_state.student_email = email
                    st.session_state.student_phone = phone
                    st.session_state.page = 'assessment'
                    st.rerun()
        
        with col_back:
            if st.button("Back", use_container_width=True):
                st.session_state.page = 'home'
                st.rerun()
    
    with col2:
        st.subheader("Assessment Details")
        st.markdown("""
        Format: Multiple Choice (MCQ)
        
        Total Questions: 15
        
        Time: 30 minutes
        
        Score: 1 point per correct answer
        
        Pass Mark: 10 points (67%)
        
        Topics Covered:
        - AI Concepts
        - Machine Learning
        - Prompt Engineering
        - Financial Analysis
        - Audit & Taxation
        - Ethical AI Use
        """)

def assessment_page():
    st.markdown(f"""
        <div class="header-container">
            <h1>📋 CA AI Training - Day 1 Assessment</h1>
            <p>Student: <b>{st.session_state.student_name}</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    total_q = len(mcq_data)
    answered = len([v for v in st.session_state.responses.values() if v])
    progress = answered / total_q if total_q > 0 else 0
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progress)
    with col2:
        st.metric("Progress", f"{answered}/{total_q}")
    
    st.write("---")
    
    for q_num, q_data in mcq_data.items():
        with st.expander(f"Q{q_num}: {q_data['topic']} [{q_data['difficulty']}]"):
            st.write(q_data['question'])
            
            selected = st.radio(
                label="Select your answer:",
                options=['a', 'b', 'c', 'd'],
                format_func=lambda x: f"{x.upper()}) {q_data['options'][x]}",
                key=f"q_{q_num}",
                label_visibility="collapsed"
            )
            
            st.session_state.responses[str(q_num)] = selected
    
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("Submit Assessment", use_container_width=True):
            if len(st.session_state.responses) == total_q:
                st.session_state.page = 'results'
                st.rerun()
            else:
                st.error(f"Please answer all {total_q} questions")

def results_page():
    score, correct_answers = calculate_score(st.session_state.responses)
    total_q = len(mcq_data)
    percentage = (score / total_q) * 100 if total_q > 0 else 0
    
    filename = save_response(
        st.session_state.student_email,
        st.session_state.responses,
        st.session_state.student_name,
        st.session_state.student_phone
    )
    
    st.markdown(f"""
        <div class="header-container">
            <h1>📊 Your Results</h1>
            <p>Student: <b>{st.session_state.student_name}</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score}/{total_q}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        status = "PASSED" if score >= 10 else "FAILED"
        st.metric("Status", status)
    
    st.write("---")
    
    if score >= 13:
        st.markdown("""
            <div class="success-box">
            <h3>Excellent Performance!</h3>
            <p>You have demonstrated excellent understanding of AI concepts. Ready for advanced applications!</p>
            </div>
        """, unsafe_allow_html=True)
    elif score >= 10:
        st.markdown("""
            <div class="success-box">
            <h3>Passed!</h3>
            <p>You have met the competency level. Review incorrect answers before applying to practice.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="error-box">
            <h3>Below Passing</h3>
            <p>Review the material and try again. Foundation in AI concepts is essential.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    
    st.subheader("Answer Review")
    
    for q_num in sorted(mcq_data.keys()):
        your = st.session_state.responses.get(str(q_num), 'N/A')
        correct = correct_answers.get(q_num, 'N/A')
        is_correct = your == correct
        
        box = f"""
        <div class="{'success-box' if is_correct else 'error-box'}">
        <h4>Q{q_num}: {mcq_data[q_num]['topic']}</h4>
        <p><b>Your:</b> {your.upper()}) {mcq_data[q_num]['options'].get(your, 'N/A')}</p>
        <p><b>Correct:</b> {correct.upper()}) {mcq_data[q_num]['options'][correct]}</p>
        <p>{'Correct' if is_correct else 'Incorrect'}</p>
        </div>
        """
        st.markdown(box, unsafe_allow_html=True)
    
    st.write("---")
    
    if st.button("Retake Assessment"):
        st.session_state.responses = {}
        st.session_state.student_name = ""
        st.session_state.student_email = ""
        st.session_state.student_phone = ""
        st.session_state.page = 'home'
        st.rerun()

def instructor_login_page():
    st.markdown("""
        <div class="instructor-header">
            <h1>Instructor Portal</h1>
            <p>Access Student Analytics</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Login")
        
        password = st.text_input("Password:", type="password", placeholder="Enter password")
        
        col_login, col_back = st.columns(2)
        
        with col_login:
            if st.button("Login", use_container_width=True):
                if password == "admin123":
                    st.session_state.instructor_authenticated = True
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Invalid password!")
        
        with col_back:
            if st.button("Back", use_container_width=True):
                st.session_state.page = 'home'
                st.rerun()
    
    with col2:
        st.info("""
        Default Credentials:
        
        Password: admin123
        
        Change this in production!
        """)

def dashboard_page():
    if not st.session_state.instructor_authenticated:
        st.error("Not authenticated. Please login first.")
        st.stop()
    
    st.markdown("""
        <div class="instructor-header">
            <h1>Instructor Dashboard</h1>
            <p>Student Performance Analytics</p>
        </div>
    """, unsafe_allow_html=True)
    
    all_responses = load_all_responses()
    
    if not all_responses:
        st.warning("No student data yet.")
        if st.button("Back to Home"):
            st.session_state.instructor_authenticated = False
            st.session_state.page = 'home'
            st.rerun()
        return
    
    scores = []
    topics = defaultdict(lambda: {'correct': 0, 'total': 0})
    students = []
    
    for resp in all_responses:
        responses = resp.get('responses', {})
        score, _ = calculate_score(responses)
        pct = (score / len(mcq_data)) * 100
        scores.append(pct)
        
        students.append({
            'Name': resp.get('name', 'N/A'),
            'Email': resp.get('email', 'N/A'),
            'Phone': resp.get('phone', 'N/A'),
            'Score': f"{score}/{len(mcq_data)}",
            'Percentage': f"{pct:.1f}%",
            'Status': 'PASSED' if score >= 10 else 'FAILED'
        })
        
        for q_num, ans in responses.items():
            q_num = int(q_num)
            topic = mcq_data[q_num]['topic']
            topics[topic]['total'] += 1
            if ans == mcq_data[q_num]['correct']:
                topics[topic]['correct'] += 1
    
    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Students", len(all_responses))
    with col2:
        avg = sum(scores) / len(scores) if scores else 0
        st.metric("Avg Score", f"{avg:.1f}%")
    with col3:
        passed = len([s for s in scores if s >= 67])
        st.metric("Passed", f"{passed}/{len(scores)}")
    with col4:
        highest = max(scores) if scores else 0
        st.metric("Highest", f"{highest:.1f}%")
    
    st.write("---")
    
    st.subheader("Score Distribution")
    score_df = pd.DataFrame({'Score %': scores})
    st.bar_chart(score_df)
    
    st.write("---")
    
    st.subheader("Topic Performance")
    topic_list = []
    for topic, stats in sorted(topics.items()):
        if stats['total'] > 0:
            pct = (stats['correct'] / stats['total']) * 100
            topic_list.append({'Topic': topic, 'Percentage': pct})
    
    if topic_list:
        topic_df = pd.DataFrame(topic_list)
        st.bar_chart(topic_df.set_index('Topic'))
    
    st.write("---")
    
    st.subheader("Students")
    st.dataframe(pd.DataFrame(students), use_container_width=True, hide_index=True)
    
    st.write("---")
    
    st.subheader("Export")
    csv = pd.DataFrame(students).to_csv(index=False)
    st.download_button(
        "Download CSV",
        data=csv,
        file_name=f"students_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    if st.button("Back to Home"):
        st.session_state.instructor_authenticated = False
        st.session_state.page = 'home'
        st.rerun()

if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'student_login':
    student_login_page()
elif st.session_state.page == 'assessment':
    assessment_page()
elif st.session_state.page == 'results':
    results_page()
elif st.session_state.page == 'instructor_login':
    instructor_login_page()
elif st.session_state.page == 'dashboard':
    dashboard_page()
else:
    st.session_state.page = 'home'
    st.rerun()
