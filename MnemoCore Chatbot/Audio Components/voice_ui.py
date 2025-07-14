# voice_ui.py
import streamlit as st
import streamlit.components.v1 as components

def record_audio_component():
    st.markdown(
        """
        <style>
        textarea[data-baseweb="textarea"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    components.html(
        """
        <div>
            <button id="startBtn">🎙️ Start Recording</button>
            <button id="stopBtn">⏹️ Stop</button>
            <audio id="audio_player" controls style="display:none;"></audio>
        </div>
        <script>
        let recorder;
        let audioChunks;

        document.getElementById("startBtn").addEventListener("click", async () => {
            audioChunks = [];
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            recorder = new MediaRecorder(stream);

            recorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            recorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

                // Display playback
                const player = document.getElementById("audio_player");
                player.src = URL.createObjectURL(audioBlob);
                player.style.display = "block";

                // Send base64 to Streamlit
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    const base64Audio = reader.result.split(',')[1];
                    const textarea = window.parent.document.querySelector('textarea');
                    textarea.value = base64Audio;
                    textarea.dispatchEvent(new Event('change', { bubbles: true }));
                };
            };

            recorder.start();
        });

        document.getElementById("stopBtn").addEventListener("click", () => {
            if (recorder && recorder.state !== "inactive") {
                recorder.stop();
            }
        });
        </script>
        """,
        height=200,
    )
