"""
modules/authentication.py - Login, Registration, Logout UI
"""
import bcrypt
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import create_user, get_user_by_username, update_last_login


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def show_auth_page():
    """Display the login / registration UI. Returns True if authenticated."""
    st.markdown("""
    <style>
    .auth-title{font-size:2.2rem;font-weight:800;color:#e94560;text-align:center;margin-bottom:4px;}
    .auth-sub{text-align:center;color:#aaa;margin-bottom:24px;}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-title">🚨 AccidentAI</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">AI-Based Road Accident Detection System</div>', unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                if submitted:
                    if not username or not password:
                        st.error("Please fill all fields.")
                    else:
                        user = get_user_by_username(username)
                        if user and verify_password(password, user["password_hash"]):
                            st.session_state["authenticated"] = True
                            st.session_state["user_id"]       = user["id"]
                            st.session_state["username"]      = user["username"]
                            update_last_login(user["id"])
                            st.success("Login successful! Redirecting…")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")

        with tab_reg:
            with st.form("register_form"):
                new_user  = st.text_input("Username", placeholder="Choose a username", key="ru")
                new_email = st.text_input("Email",    placeholder="your@email.com",    key="re")
                new_pass  = st.text_input("Password", type="password",                 key="rp")
                new_pass2 = st.text_input("Confirm Password", type="password",         key="rp2")
                reg_btn   = st.form_submit_button("Register", use_container_width=True)
                if reg_btn:
                    if not all([new_user, new_email, new_pass, new_pass2]):
                        st.error("Please fill all fields.")
                    elif new_pass != new_pass2:
                        st.error("Passwords do not match.")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        ok, msg = create_user(new_user, new_email, hash_password(new_pass))
                        if ok:
                            st.success("Account created! Please login.")
                        else:
                            st.error(f"Registration failed: {msg}")

    return st.session_state.get("authenticated", False)


def logout():
    for key in ["authenticated", "user_id", "username"]:
        st.session_state.pop(key, None)
    st.rerun()
