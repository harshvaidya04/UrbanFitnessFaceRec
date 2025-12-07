import streamlit as st
from PIL import Image

# Set page configuration
st.set_page_config(page_title='Urban Fitness Gym', layout='wide')

# Display header and welcome message
st.title('Urban Fitness Gym')
st.subheader("Welcome to the Attendance System using Face Recognition")

# Display gym image
gym_image = Image.open('gym.jpg')
st.image(gym_image, caption='Stay Fit, Stay Healthy!', use_column_width=True)

# Add navigation options
st.markdown("## What would you like to do?")

# Create buttons for navigation
col1, col2 = st.columns(2)

with col1:
    if st.button('Register Your Face'):
        st.info("Navigate to the Registration Form to register your face.")
        st.markdown("[Go to Registration Form](./pages/2_Registration_form.py)")

with col2:
    if st.button('Mark Attendance'):
        st.info("Navigate to Real-Time Prediction to mark your attendance.")
        st.markdown("[Go to Real-Time Prediction](./pages/1_Real_Time_Prediction.py)")

# Footer
st.markdown("---")
st.caption("Urban Fitness Gym - Powered by Face Recognition Technology")



