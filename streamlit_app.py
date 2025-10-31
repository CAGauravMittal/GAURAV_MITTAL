import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import re
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="CA AI Training - Day 1 Assessment",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create responses directory
Path("responses").mkdir(exist_ok=True)

# Custom CSS for better styling
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
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        padding: 15px;
        border-radius: 8px;
        color: #856404;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 15px;
        border-radius: 8px;
        color: #721c24;
    }
    @media (max-width: 768px) {
        .header-container {
            padding: 10px;
        }
        .question-box {
            padding: 10px;
            margin: 10px 0;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state with proper defaults
def init_session_state():
    """Initialize all session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'student_email' not in st.session_state:
        st.session_state.student_email = ""
    if 'student_phone' not in st.session_state:
        st.session_state.student_phone = ""
    if 'start_time' not in st.session_state:
        st.session_state.start_time = datetime.now()

init_session_state()

# Validation functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (10 digits for India)"""
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    """Validate name (at least 3 characters)"""
    return len(name.strip()) >= 3 and name.isalpha() or ' ' in name

# MCQ Data (15 questions)
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
            'a': "\"Check if expenses are valid\"",
            'b': "\"You are internal audit partner. Review attached 300 expense reports against this policy:\n- Flight: Only first class for flights >4 hours (max ₹1,20,000/ticket)\n- Hotel: Max ₹12,000/night, 3-star or below\n- Meals: ₹800/day per diem, or receipt reimbursement\n- Entertainment: Client entertainment ₹5,000/person max\n\nFlag: (1) Policy violations (2) Borderline cases (3) Risk indicators.\nFormat: Excel-ready table with columns: Employee, Amount, Policy, Violation Type, Recommended Action, Manager\"",
            'c': "\"Analyze expenses and tell me if anything is wrong\"",
            'd': "\"Use machine learning to predict which employees will submit fraudulent expenses\""
        },
        'correct': 'b',
        'topic': 'Prompt Engineering',
        'difficulty': 'Medium'
    },
    4: {
        'question': "Reinforcement Learning - Tally Integration\n\nYour firm has Tally Prime with ODBC enabled. You want to build a system that learns to automatically flag suspicious journal entries. How would reinforcement learning help in this scenario?",
        'options': {
            'a': "Show the system 100 examples of legitimate journal entries and it will reject all others",
            'b': "The system flags all unusual entries, gets feedback monthly from partner (\"This was fraud\" or \"This was legitimate\"), adjusts thresholds quarterly to improve accuracy",
            'c': "Use past audit findings only; no need for ongoing learning",
            'd': "This is supervised learning, not reinforcement learning"
        },
        'correct': 'b',
        'topic': 'Reinforcement Learning',
        'difficulty': 'Hard'
    },
    5: {
        'question': "Bias in AI - Audit Risk Assessment\n\nAn AI audit tool, trained on 10 years of firm's audit data, consistently flags \"transactions >₹20 lakhs from certain vendors as high-risk\" while flagging \"transactions >₹50 lakhs from established vendors as low-risk.\" What is the PRIMARY concern?",
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
        'question': "Month-End Close Automation\n\nA CFO of ₹500 cr revenue manufacturing company has this month-end close process:\n- Tally exports (manual): 20 min\n- Variance analysis: 40 min\n- Expense accruals: 30 min\n- Manual commenting: 30 min\nTotal: 120 min/month\n\nUsing Tally ODBC + Power BI + ChatGPT API integration, after 2-day setup, what is REALISTIC outcome by month 2?",
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
        'question': "Expense Reconciliation - Compliance Issue\n\nA startup's expense data shows:\n- Employee Rakesh submitted 5 hotel bills from \"Hotel Paradise\" at exactly ₹12,000/night for 20 consecutive days\n- Policy allows ₹12,000/night max\n- All within policy technically\n- But statistically, staying in same 3-star hotel for 20 days at EXACTLY policy limit is highly unusual\n\nWhat should an AI auditing tool flag here?",
        'options': {
            'a': "No issue - all within policy limits",
            'b': "\"SUSPICIOUS PATTERN: Consistent exact-limit compliance across 20 days suggests potential fabrication of expenses. Recommend: (1) Verify hotel receipts and stay dates (2) Check travel project dates (3) Review employee's travel pattern\"",
            'c': "Approve all 20 days - employee is budget-conscious",
            'd': "Flag only if even ONE day exceeds policy"
        },
        'correct': 'b',
        'topic': 'Anomaly Detection',
        'difficulty': 'Medium'
    },
    8: {
        'question': "AI for Month-End Accruals\n\nA ₹200 cr IT services company has complex accruals: employee bonuses (variable), warranty provisions (estimated), project revenue adjustments (percentage complete method). CFO currently spends 6 hours monthly calculating these accruals.\n\nUsing Tally database + ODBC connection to AI (ChatGPT with Excel), what is MOST feasible for automation?",
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
        'question': "Anomaly in Financial Data\n\nAudit of Fintech startup \"PayQuick Ltd\" (FY 2024-25):\n- Monthly revenue Oct-Dec 2024: ₹8cr, ₹8.5cr, ₹9cr (steady)\n- January 2025: ₹22cr (145% jump)\n- Feb-Mar 2025: ₹9.5cr, ₹10cr (back to normal)\n\nCompany claims \"January was product launch month in new market (Singapore)\". Management has provided:\n- ₹22cr revenue from 3 Singapore customers\n- Singapore customer PAN numbers (seems odd for foreign customers)\n- No documentation of market research, customer negotiations, or product adaptation costs\n\nAs auditor using AI for anomaly detection, what is your NEXT step?",
        'options': {
            'a': "Accept explanation - this is normal in fintech startup; approve revenue",
            'b': "Flag for investigation: \"Large one-time revenue from new market; verify: (1) Customer legitimacy (are these real entities or related parties?) (2) Performance obligations (what was delivered?) (3) Collection (has payment been received?) (4) Why no repeat in Feb?\"",
            'c': "Reject revenue - startups can't have such large deals",
            'd': "This isn't an audit issue; focus on other areas"
        },
        'correct': 'b',
        'topic': 'Revenue Anomaly',
        'difficulty': 'Hard'
    },
    10: {
        'question': "GST Compliance Automation\n\nYour firm audits a ₹150cr distributor with operations in Maharashtra, Gujarat, Tamil Nadu, Delhi. GST compliance check currently takes 40 hours/month (GSTR-1 vs GSTR-2B vs sales register reconciliation).\n\nUsing Power BI + Tally ODBC + ChatGPT for GST analysis, what's the expected timeline for implementation?",
        'options': {
            'a': "Week 1: Connect Tally ODBC to Power BI; Week 2: Build GST reconciliation dashboard; Week 3: AI prompts for compliance analysis\nResult: 40 hours → 8-10 hours/month (75% reduction)",
            'b': "Week 1-2: Build automated reconciliation; Week 3: Train team\nResult: 40 hours → 15-20 hours/month (60% reduction) for first month",
            'c': "Day 1: Connect; Day 2-7: Testing; Week 2: Go-live\nResult: 40 hours → 2-3 hours/month (95% reduction)",
            'd': "Too complex; manual process more reliable"
        },
        'correct': 'a',
        'topic': 'GST Automation',
        'difficulty': 'Hard'
    },
    11: {
        'question': "Transfer Pricing in Digital Economy\n\nYour client \"CloudServe India\" (IT services) has this structure:\n- India entity: Develops software (costs ₹50 lakhs)\n- US entity (Delaware corp): Sells to US customers as SaaS (charges $10,000/month × 50 customers = ₹40+ crore annual revenue)\n- TP arrangement: India charges US entity ₹50 lakhs annually for development + support\n\nIncome Tax Department challenges this TP (says underpriced). What should AI-assisted TP analysis focus on?",
        'options': {
            'a': "Accept current TP; no need to adjust",
            'b': "Analyze: (1) What do comparable IT companies charge for similar SaaS development? (Benchmarking) (2) What % of US revenue should India entity receive for its contribution? (Economic analysis) (3) What functions does India entity perform vs US entity? (FAR analysis) (4) Is TP defensible under Indian TP rules?",
            'c': "Just increase India's charge to ₹2 crore to be safe",
            'd': "Don't engage with IT Dept; dispute everything"
        },
        'correct': 'b',
        'topic': 'Transfer Pricing',
        'difficulty': 'Hard'
    },
    12: {
        'question': "Going Concern Assessment\n\nManufacturing company \"SteelTech Ltd\" audit:\n- Revenue FY24: ₹200cr; FY25: ₹180cr (declining)\n- Net loss FY25: ₹20cr (vs ₹15cr profit prior year)\n- Bank balance: ₹5cr (down from ₹50cr)\n- Debt due in 12 months: ₹80cr\n- Current ratio: 0.4\n\nBUT: Management has obtained:\n- Letter of credit from Development Bank for ₹60cr (to refinance debt)\n- New order from Govt of India for ₹150cr (contract signed, 2-year delivery)\n\nWhat is the CORRECT audit opinion approach?",
        'options': {
            'a': "Adverse opinion - company clearly insolvent",
            'b': "Unqualified opinion with Emphasis of Matter paragraph: \"Going concern depends on loan refinancing and Govt contract execution. These are contingencies with execution risk. Management has disclosed this. Auditor satisfied with disclosure.\"",
            'c': "Qualified opinion - too much uncertainty",
            'd': "No going concern issue - Govt orders are guaranteed"
        },
        'correct': 'b',
        'topic': 'Going Concern',
        'difficulty': 'Hard'
    },
    13: {
        'question': "Bank Reconciliation - Automation with ODBC\n\nYour firm uses Tally + Power BI ODBC automation for monthly bank reconciliation of 3 bank accounts (company has ₹500cr+ cash).\n\nAutomated system flags:\n- ₹50 lakhs: Bank transfer from unknown entity dated 30th Sept, marked as \"investment income\" but not requested by company\n- Settlement clearing in bank statement for transaction posted in Tally but dated 3 months ago\n\nWhat is CORRECT audit action?",
        'options': {
            'a': "Ignore - reconciliation matches; no further testing needed",
            'b': "Investigate BOTH: (1) Is ₹50 lakh receipt legitimate or fraudulent? (2) Why 3-month delay in settlement? Could indicate backdated transaction or manipulation. Require management explanation + supporting documentation.",
            'c': "Approve reconciliation - computer says it matches",
            'd': "These are timing differences; routine"
        },
        'correct': 'b',
        'topic': 'Bank Reconciliation',
        'difficulty': 'Hard'
    },
    14: {
        'question': "Data Security Breach Scenario\n\nYou're using ChatGPT to analyze a client's expense dataset for variance analysis. You paste the following:\n\n\"Employees with highest expenses: Rajesh (CEO) ₹45,00,000 (includes 10 international trips, 5-star hotels, first-class flights), Priya (CFO) ₹22,00,000, Amit (CTO) ₹18,00,000. Total 50 employees, total spend ₹3,50,00,000...\"\n\nWhat is the PROFESSIONAL ERROR here?",
        'options': {
            'a': "None - this is aggregate data",
            'b': "You've identified specific individuals (Rajesh, Priya, Amit) by name, function, and amounts. This is CONFIDENTIAL client information. Even ChatGPT's free version may use inputs for training. BREACH.",
            'c': "Using ChatGPT for any client analysis is fine; this is normal practice",
            'd': "Only problem if you pasted the ENTIRE report, not summary"
        },
        'correct': 'b',
        'topic': 'Data Security',
        'difficulty': 'Medium'
    },
    15: {
        'question': "AI Hallucination - Tax Scenario\n\nA client asks you: \"Can we claim 100% deduction for consulting fees paid to Group's Singapore entity under Section 37(1)?\"\n\nUsing ChatGPT, you get response: \"Yes, Section 37(1) allows 100% deduction for ordinary and necessary business expenses, including consulting fees to related entities. Singapore entity should issue invoice.\"\n\nBefore advising the client, you verify this with:\n- Current Income Tax Act Section 37(1) [actual rule]\n- Section 40A (Transfer Pricing compliance required for related party payments)\n- Section 92 (Actual TP study required for payments >₹5 cr)\n\nWhat do you discover?",
        'options': {
            'a': "ChatGPT was correct - 100% deduction allowed",
            'b': "ChatGPT hallucinated: While Section 37(1) allows deduction, it requires:\n   - Invoice on proper letterhead with tax ID\n   - Transfer pricing documentation (Section 92)\n   - TP study proving it's arm's length rate\n   - NO automatic 100% deduction without these",
            'c': "Deduction is denied - can't pay related parties",
            'd': "This is too complex for AI; don't use AI for tax"
        },
        'correct': 'b',
        'topic': 'AI Hallucination',
        'difficulty': 'Hard'
    }
}

def save_response_cloud(email, responses, student_name, student_phone):
    """Save responses to cloud-compatible JSON"""
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
        st.error(f"❌ Error saving response: {str(e)}")
        return None

def calculate_score(responses):
    """Calculate score and return details"""
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
        st.error(f"❌ Error calculating score: {str(e)}")
        return 0, {}

def login_page():
    """Login page for student information"""
    st.markdown("""
        <div class="header-container">
            <h1>📋 CA AI Training - Day 1 Assessment</h1>
            <p style='font-size: 18px; margin: 10px 0;'>MCQ Assessment for Chartered Accountants</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Student Information")
        
        name = st.text_input(
            "Full Name *",
            placeholder="Enter your full name",
            key="student_name_input"
        )
        
        email = st.text_input(
            "Email ID *",
            placeholder="Enter your email (e.g., student@example.com)",
            key="student_email_input"
        )
        
        phone = st.text_input(
            "Phone Number *",
            placeholder="Enter your phone number (10 digits)",
            key="student_phone_input"
        )
        
        st.write("---")
        
        col_submit, col_info = st.columns([1, 1])
        
        with col_submit:
            if st.button("▶️ Start Assessment", use_container_width=True):
                # Validation
                errors = []
                
                if not validate_name(name):
                    errors.append("❌ Name must be at least 3 characters (letters and spaces only)")
                
                if not validate_email(email):
                    errors.append("❌ Invalid email format (e.g., student@example.com)")
                
                if not validate_phone(phone):
                    errors.append("❌ Phone number must be 10 digits")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    st.session_state.student_name = name
                    st.session_state.student_email = email
                    st.session_state.student_phone = phone
                    st.session_state.page = 'assessment'
                    st.session_state.start_time = datetime.now()
                    st.rerun()
        
        with col_info:
            st.info("ℹ️ All fields are required and validated")
    
    with col2:
        st.subheader("📚 Assessment Details")
        
        details_md = """
        **Format:** Multiple Choice Questions (MCQ)
        
        **Total Questions:** 15
        
        **Time Limit:** 30 minutes
        
        **Scoring:** 1 point per correct answer
        
        **Maximum Score:** 15 points
        
        **Passing Score:** 10 points (67%)
        
        ---
        
        **Topics Covered:**
        - AI Concepts & Evolution
        - Machine Learning Applications
        - Prompt Engineering
        - Financial Analysis with AI
        - Audit & Taxation
        - Ethical AI Use
        """
        
        st.markdown(details_md)

def assessment_page():
    """Assessment page with MCQs"""
    st.markdown(f"""
        <div class="header-container">
            <h1>📋 CA AI Training - Day 1 Assessment</h1>
            <p>Student: <b>{st.session_state.student_name}</b> | Email: {st.session_state.student_email}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Progress tracking
    total_questions = len(mcq_data)
    answered_count = len([v for v in st.session_state.responses.values() if v])
    progress = answered_count / total_questions if total_questions > 0 else 0
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progress)
    with col2:
        st.metric("Progress", f"{answered_count}/{total_questions}")
    
    st.write("---")
    
    # Display all questions with expanders
    for q_num, q_data in mcq_data.items():
        with st.expander(f"Question {q_num}: {q_data['topic']} [{q_data['difficulty']}]"):
            st.write(q_data['question'])
            
            selected_option = st.radio(
                label="Select your answer:",
                options=['a', 'b', 'c', 'd'],
                format_func=lambda x: f"{x.upper()}) {q_data['options'][x]}",
                key=f"q_{q_num}",
                label_visibility="collapsed"
            )
            
            st.session_state.responses[str(q_num)] = selected_option
    
    st.write("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("✅ Submit Assessment", use_container_width=True):
            if len(st.session_state.responses) == total_questions:
                st.session_state.page = 'results'
                st.rerun()
            else:
                st.error(f"❌ Please answer all {total_questions} questions before submitting")

def results_page():
    """Results page with score and feedback"""
    score, correct_answers = calculate_score(st.session_state.responses)
    total_questions = len(mcq_data)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Save responses
    filename = save_response_cloud(
        st.session_state.student_email,
        st.session_state.responses,
        st.session_state.student_name,
        st.session_state.student_phone
    )
    
    st.markdown(f"""
        <div class="header-container">
            <h1>📊 Assessment Results</h1>
            <p>Student: <b>{st.session_state.student_name}</b> | Email: {st.session_state.student_email}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score", f"{score}/{total_questions}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        status = "✅ PASSED" if score >= 10 else "❌ FAILED"
        st.metric("Status", status)
    
    st.write("---")
    
    # Interpretation
    if score >= 13:
        st.markdown("""
            <div class="success-box">
            <h3>🎉 Excellent Performance!</h3>
            <p>Your understanding of AI concepts and their practical application in CA practice is excellent. You're ready for advanced AI applications in audit and taxation work.</p>
            </div>
        """, unsafe_allow_html=True)
    elif score >= 10:
        st.markdown("""
            <div class="success-box">
            <h3>✅ Satisfactory Performance</h3>
            <p>You've met the minimum competency level. Review the incorrect answers to strengthen your understanding before applying AI in client work.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="error-box">
            <h3>⚠️ Below Passing Score</h3>
            <p>Review the session material and incorrect answers. Strong foundation in AI concepts is essential before applying to professional practice.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    
    # Detailed feedback
    st.subheader("📋 Detailed Answer Review")
    
    for q_num in sorted(mcq_data.keys()):
        your_answer = st.session_state.responses.get(str(q_num), 'N/A')
        correct_answer = correct_answers.get(q_num, 'N/A')
        is_correct = your_answer == correct_answer
        
        question_box = f"""
        <div class="{'success-box' if is_correct else 'error-box'}">
        <h4>Question {q_num}: {mcq_data[q_num]['topic']}</h4>
        <p><b>Your Answer:</b> {your_answer.upper()}) {mcq_data[q_num]['options'].get(your_answer, 'Not answered')}</p>
        <p><b>Correct Answer:</b> {correct_answer.upper()}) {mcq_data[q_num]['options'][correct_answer]}</p>
        <p><b>Status:</b> {'✅ Correct' if is_correct else '❌ Incorrect'}</p>
        </div>
        """
        
        st.markdown(question_box, unsafe_allow_html=True)
    
    st.write("---")
    
    st.subheader("📥 Results Saved")
    
    if filename:
        st.success(f"✅ Results successfully saved!")
        st.info(f"📄 File: {filename}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Retake Assessment"):
            st.session_state.page = 'login'
            st.session_state.responses = {}
            st.session_state.submitted = False
            st.session_state.student_name = ""
            st.session_state.student_email = ""
            st.session_state.student_phone = ""
            st.rerun()
    
    with col2:
        st.info("✅ Assessment complete! Thank you for participating.")

# Main app logic
if st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'assessment':
    assessment_page()
elif st.session_state.page == 'results':
    results_page()
