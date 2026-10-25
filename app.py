import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import secrets

ROOT = Path(__file__).parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
SESSIONS = DATA / 'sessions.csv'
ATTENDANCE = DATA / 'attendance.csv'
PARTICIPATION = DATA / 'participation.csv'


def read_csv(path, columns):
    if path.exists():
        try:
            return pd.read_csv(path).reindex(columns=columns)
        except Exception:
            pass
    return pd.DataFrame(columns=columns)


def save_row(path, row, columns):
    df = read_csv(path, columns)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)

sessions_cols = ['session_id', 'course', 'topic', 'session_date', 'created_at']
attendance_cols = ['session_id', 'student_id', 'student_name', 'checkin_time', 'method']
participation_cols = ['session_id', 'student_id', 'signal_type', 'count', 'notes', 'recorded_at']

st.set_page_config(page_title='Multimodal Attendance & Engagement Agent', page_icon='🎓', layout='wide')
st.title('🎓 Multimodal Attendance & Engagement Agent')
st.caption('A privacy-conscious classroom analytics MVP for attendance, participation, and session summaries.')
st.info('Privacy by design: this demo uses QR/token-style check-ins and teacher-entered participation signals. It does not identify faces, infer emotions, or record classroom audio/video.')

sessions = read_csv(SESSIONS, sessions_cols)
attendance = read_csv(ATTENDANCE, attendance_cols)
participation = read_csv(PARTICIPATION, participation_cols)

tab1, tab2, tab3, tab4 = st.tabs(['Dashboard', 'Create session', 'Record attendance', 'Participation & reports'])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Sessions', len(sessions))
    c2.metric('Attendance check-ins', len(attendance))
    c3.metric('Students represented', attendance['student_id'].nunique() if not attendance.empty else 0)
    c4.metric('Participation entries', len(participation))
    if not sessions.empty:
        st.subheader('Recent sessions')
        st.dataframe(sessions.sort_values('created_at', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.write('Create your first session in the **Create session** tab to get started.')
    if not attendance.empty:
        st.subheader('Attendance by session')
        counts = attendance.groupby('session_id', as_index=False).agg(checked_in=('student_id', 'nunique'))
        st.bar_chart(counts.set_index('session_id'))

with tab2:
    st.subheader('Create a class session')
    with st.form('create_session'):
        course = st.text_input('Course / class name', placeholder='e.g., Data Science')
        topic = st.text_input('Session topic', placeholder='e.g., Introduction to Machine Learning')
        session_date = st.date_input('Session date', value=date.today())
        create = st.form_submit_button('Create session', type='primary')
    if create:
        if not course.strip() or not topic.strip():
            st.error('Please enter both course name and topic.')
        else:
            sid = secrets.token_hex(3).upper()
            save_row(SESSIONS, {'session_id': sid, 'course': course.strip(), 'topic': topic.strip(), 'session_date': str(session_date), 'created_at': datetime.now().isoformat(timespec='seconds')}, sessions_cols)
            st.success(f'Session created. Session code: {sid}')
            st.caption('Share this session code with the class. For a production deployment, use authenticated accounts and expiring QR tokens.')
            st.rerun()

with tab3:
    st.subheader('Record attendance')
    sessions = read_csv(SESSIONS, sessions_cols)
    if sessions.empty:
        st.warning('Create a session first.')
    else:
        options = {f"{r.session_id} — {r.course}: {r.topic}": r.session_id for r in sessions.itertuples()}
        selected = st.selectbox('Select session', list(options.keys()), key='attendance_session')
        with st.form('checkin_form'):
            student_id = st.text_input('Student ID', placeholder='e.g., CSE1024')
            student_name = st.text_input('Student name')
            method = st.selectbox('Check-in method', ['Session code', 'Teacher verified', 'QR check-in (prototype)'])
            submitted = st.form_submit_button('Mark present', type='primary')
        if submitted:
            sid = options[selected]
            if not student_id.strip() or not student_name.strip():
                st.error('Enter student ID and name.')
            elif ((attendance['session_id'] == sid) & (attendance['student_id'].astype(str).str.casefold() == student_id.strip().casefold())).any():
                st.warning('This student is already marked present for this session.')
            else:
                save_row(ATTENDANCE, {'session_id': sid, 'student_id': student_id.strip(), 'student_name': student_name.strip(), 'checkin_time': datetime.now().isoformat(timespec='seconds'), 'method': method}, attendance_cols)
                st.success('Attendance recorded.')
                st.rerun()
        current = read_csv(ATTENDANCE, attendance_cols)
        current = current[current['session_id'] == options[selected]]
        st.dataframe(current, use_container_width=True, hide_index=True)
        if not current.empty:
            st.download_button('Download this session attendance CSV', current.to_csv(index=False).encode('utf-8'), file_name=f'attendance_{options[selected]}.csv', mime='text/csv')

with tab4:
    st.subheader('Record participation signals')
    sessions = read_csv(SESSIONS, sessions_cols)
    attendance = read_csv(ATTENDANCE, attendance_cols)
    if sessions.empty:
        st.warning('Create a session first.')
    else:
        options = {f"{r.session_id} — {r.course}: {r.topic}": r.session_id for r in sessions.itertuples()}
        selected = st.selectbox('Session for participation', list(options.keys()), key='participation_session')
        sid = options[selected]
        roster = attendance[attendance['session_id'] == sid]
        if roster.empty:
            st.caption('No attendance recorded for this session yet. You can still enter a student ID manually.')
        known = roster['student_id'].astype(str).tolist() if not roster.empty else []
        with st.form('participation_form'):
            pid = st.selectbox('Student ID', known + ['Enter another ID']) if known else 'Enter another ID'
            if pid == 'Enter another ID':
                pid = st.text_input('Student ID (manual)', key='manual_pid')
            signal = st.selectbox('Participation signal', ['Asked a question', 'Answered a question', 'Group activity contribution', 'Poll response', 'Task completed'])
            count = st.number_input('Count', min_value=1, max_value=100, value=1)
            notes = st.text_input('Optional brief note (avoid sensitive personal details)')
            add = st.form_submit_button('Save participation')
        if add:
            if not str(pid).strip():
                st.error('Enter or select a student ID.')
            else:
                save_row(PARTICIPATION, {'session_id': sid, 'student_id': str(pid).strip(), 'signal_type': signal, 'count': int(count), 'notes': notes.strip(), 'recorded_at': datetime.now().isoformat(timespec='seconds')}, participation_cols)
                st.success('Participation signal saved.')
                st.rerun()
        participation = read_csv(PARTICIPATION, participation_cols)
        current = participation[participation['session_id'] == sid]
        if not current.empty:
            st.subheader('Participation summary')
            summary = current.groupby('signal_type', as_index=False)['count'].sum()
            st.bar_chart(summary.set_index('signal_type'))
            st.dataframe(current, use_container_width=True, hide_index=True)
            st.download_button('Download participation CSV', current.to_csv(index=False).encode('utf-8'), file_name=f'participation_{sid}.csv', mime='text/csv')
            st.caption('Counts are descriptive signals, not a score of a student’s attention, ability, or performance.')

st.divider()
st.caption('Academic prototype • Local CSV storage • Use only with institutional approval and informed consent. Add authentication, access controls, retention rules, and secure storage before real-world deployment.')
