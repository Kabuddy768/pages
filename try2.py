import streamlit as st
import firebase_admin
from firebase_admin import auth, exceptions, credentials, initialize_app
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2

# Initialize Firebase app
cred = credentials.Certificate("login1-f9b42-666927ffad75.json")
try:
    firebase_admin.get_app()
except ValueError as e:    
    initialize_app(cred)


# Initialize Google OAuth2 client
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_uri = "https://kabuddy768.github.io/new_project/"  # Your redirect URI

client = GoogleOAuth2(client_id=client_id, client_secret=client_secret)

st.set_page_config(page_title='USD/KES Analysis Page', layout='wide')

st.session_state.email = ''

async def get_access_token(client: GoogleOAuth2, redirect_uri: str, code: str):
    return await client.get_access_token(code, redirect_uri)

async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

@st.cache_data
def get_logged_in_user_email():
    try:
        query_params = st.query_params()
        code = query_params.get('code')
        if code:
            token = asyncio.run(get_access_token(client, redirect_uri, code))
            st.experimental_set_query_params()

            if token:
                
                user_id, user_email = asyncio.run(get_email(client, token['access_token']))
                if user_email:
                    try:
                        user = auth.get_user_by_email(user_email)
                    except exceptions.FirebaseError:
                        user = auth.create_user(email=user_email)
                    return user.email
        return None
    except Exception as e:
        print(e)
        return None

def show_login_button():
    authorization_url = asyncio.run(client.get_authorization_url(
        redirect_uri,
        scope=["email", "profile"],
        extras_params={"access_type": "offline"},
    ))
    st.markdown('<a href="{}" target="_self">Login with Google Account</a>'.format(authorization_url), unsafe_allow_html=True)
    email = get_logged_in_user_email()

if __name__ == "__main__":
    st.title('USD/KES Analysis Page')
    if not st.session_state.email:
        show_login_button()
    else:
        st.subheader(f"Hello, {st.session_state.email}")
        if st.button("Logout", type="primary"):
            st.session_state.email = ''
            st.experimental_rerun()