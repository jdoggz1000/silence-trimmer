import streamlit as st
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
import io
import zipfile

# --- CORE LOGIC ---
def trim_tail_silence(audio_segment, silence_threshold=-50.0, chunk_size=10):
    """
    Reverses audio, trims the 'leading' silence (which is the tail),
    and reverses it back.
    """
    reversed_sound = audio_segment.reverse()
    silence_duration = detect_leading_silence(
        reversed_sound, 
        silence_threshold=silence_threshold, 
        chunk_size=chunk_size
    )
    # Return the trimmed audio
    return reversed_sound[silence_duration:].reverse()

# --- APP INTERFACE ---
st.title("✂️ Ghost Silence Trimmer")
st.write("Upload your ElevenLabs/AI audio to strip the trailing silence automatically.")

# 1. File Uploader
uploaded_files = st.file_uploader(
    "Drop your audio files here (MP3 or WAV)", 
    accept_multiple_files=True, 
    type=['mp3', 'wav']
)

if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} Files"):
        
        # Create a ZIP file in memory (so we don't junk up your server with temp files)
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                # Load audio from memory
                audio = AudioSegment.from_file(file)
                
                # Trim it
                trimmed_audio = trim_tail_silence(audio)
                
                # Export to memory buffer
                output_buffer = io.BytesIO()
                file_format = file.name.split('.')[-1]
                trimmed_audio.export(output_buffer, format=file_format)
                
                # Add to ZIP
                zip_file.writestr(file.name, output_buffer.getvalue())
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
        
        # 2. Download Button
        st.success("All files trimmed!")
        st.download_button(
            label="⬇️ Download All (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="trimmed_audio.zip",
            mime="application/zip"
        )