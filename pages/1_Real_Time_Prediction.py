import streamlit as st
import cv2
import time
import av
import face_rec
from streamlit_webrtc import webrtc_streamer

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Real-Time Attendance System",
    layout="wide"
)

st.title("Real-Time Attendance System")
st.caption("Browser Webcam | Local Camera | IP / NVR (RTSP)")

# --------------------------------------------------
# Load face database
# --------------------------------------------------
with st.spinner("Loading registered faces from Redis..."):
    redis_face_db = face_rec.retrive_data("academy:register")

st.success(f"Loaded {len(redis_face_db)} registered faces")

# --------------------------------------------------
# Camera selection
# --------------------------------------------------
st.markdown("### Camera Configuration")

camera_type = st.radio(
    "Select Camera Source",
    options=[
        "Browser Webcam (WebRTC)",
        "Local Camera (USB / Pi)",
        "IP / NVR Camera (RTSP)"
    ]
)

# RTSP input (only visible when needed)
rtsp_url = None
if camera_type == "IP / NVR Camera (RTSP)":
    rtsp_url = st.text_input(
        "RTSP URL",
        placeholder="rtsp://username:password@ip:554/stream"
    )

col1, col2 = st.columns(2)
with col1:
    start_btn = st.button("▶ Start Camera", use_container_width=True)
with col2:
    stop_btn = st.button("⏹ Stop Camera", use_container_width=True)

# --------------------------------------------------
# Initialize predictor
# --------------------------------------------------
realtimepred = face_rec.RealTimePred()

WAIT_TIME = 30  # seconds
last_log_time = time.time()

# ==================================================
# OPTION 1: Browser Webcam (WebRTC)
# ==================================================
if camera_type == "Browser Webcam (WebRTC)":

    st.info("Using browser webcam via WebRTC")

    def video_frame_callback(frame):
        global last_log_time

        img = frame.to_ndarray(format="bgr24")

        pred_img = realtimepred.face_prediction(
            img,
            redis_face_db,
            feature_column="facial_features",
            name_role=["Name", "Role"],
            thresh=0.5
        )

        if time.time() - last_log_time >= WAIT_TIME:
            realtimepred.saveLogs_redis()
            last_log_time = time.time()

        return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

    webrtc_streamer(
        key="browser-webcam",
        video_frame_callback=video_frame_callback,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        }
    )

# ==================================================
# OPTION 2 & 3: OpenCV (Local / RTSP)
# ==================================================
if camera_type in ["Local Camera (USB / Pi)", "IP / NVR Camera (RTSP)"]:

    if start_btn:

        # Select video source
        if camera_type == "Local Camera (USB / Pi)":
            video_source = 0
            st.info("Using Local Camera")
        else:
            if not rtsp_url:
                st.error("Please enter a valid RTSP URL")
                st.stop()
            video_source = rtsp_url
            st.info("Using RTSP Camera / NVR")

        cap = cv2.VideoCapture(video_source, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            st.error("❌ Unable to open video source")
            st.stop()

        st.success("Camera connected successfully")

        frame_placeholder = st.empty()
        frame_count = 0

        while cap.isOpened():

            if stop_btn:
                st.warning("Camera stopped by user")
                break

            ret, frame = cap.read()
            if not ret:
                st.error("⚠️ Failed to read frame")
                break

            frame_count += 1

            # Skip frames for performance (important for Pi)
            if frame_count % 3 != 0:
                continue

            # Resize for performance
            frame = cv2.resize(frame, (640, 480))

            pred_frame = realtimepred.face_prediction(
                frame,
                redis_face_db,
                feature_column="facial_features",
                name_role=["Name", "Role"],
                thresh=0.5
            )

            if time.time() - last_log_time >= WAIT_TIME:
                realtimepred.saveLogs_redis()
                last_log_time = time.time()

            frame_placeholder.image(
                pred_frame,
                channels="BGR",
                use_column_width=True
            )

        cap.release()
        st.info("Camera connection closed")

# --------------------------------------------------
# Help section
# --------------------------------------------------
with st.expander("RTSP Examples"):
    st.code(
        """
IP Camera:
rtsp://admin:12345@192.168.1.50:554/stream1

Hikvision NVR:
rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/101

Dahua NVR:
rtsp://admin:12345@192.168.1.100:554/cam/realmonitor?channel=1&subtype=1
        """,
        language="text"
    )
