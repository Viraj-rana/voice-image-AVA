

import streamlit as st
import os
import random
from PIL import Image
import base64
import io
import pyttsx3
import speech_recognition as sr
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Voice Photo Social",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def add_logo(logo_path, width=60):
    """Add a logo to the top right corner of the app"""
    try:
        with open(logo_path, "rb") as f:
            logo_data = f.read()
        logo_base64 = base64.b64encode(logo_data).decode()
        
        logo_html = f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" width="{width}">
        </div>
        """
        st.markdown(logo_html, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load logo: {e}")

# Initialize session state
if 'last_command' not in st.session_state:
    st.session_state.last_command = ""
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'assistant_response' not in st.session_state:
    st.session_state.assistant_response = "Welcome! Upload your photos and use voice commands!"
if 'all_photos' not in st.session_state:
    st.session_state.all_photos = []

class VoicePhotoSocial:
    def __init__(self):
        self.images_base_path = "images"
        self.setup_directories()
        self.load_all_photos()
        
    def setup_directories(self):
        """Create images directory if it doesn't exist"""
        os.makedirs(self.images_base_path, exist_ok=True)
    
  from datetime import datetime
import os
from pathlib import Path
from typing import List, Dict, Any


class YourClass:  # (whatever your class name is)

    def load_all_photos(self) -> List[Dict[str, Any]]:
        """
        Load metadata of all image files from the images folder.
        
        Returns:
            List of dictionaries with photo information
        """
        photos = []
        if not os.path.exists(self.images_base_path):
            return photos

        base_path = Path(self.images_base_path)
        
        # Supported image extensions (lowercase)
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

        for entry in base_path.iterdir():
            if not entry.is_file():
                continue
                
            suffix = entry.suffix.lower()
            if suffix not in image_extensions:
                continue

            try:
                ctime = entry.stat().st_ctime
                upload_date = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d %H:%M")
                
                # Use stem → filename without extension
                person_name = entry.stem.capitalize()

                photos.append({
                    'path': str(entry),               # consistent with original
                    'filename': entry.name,
                    'name': person_name,
                    'upload_date': upload_date,
                    'size': entry.stat().st_size      # bytes
                })
                
            except (OSError, FileNotFoundError):
                # Skip files we cannot stat (deleted/moved in the meantime, permission issues...)
                continue

        # Optional: sort by upload date (newest first) – very common need
        photos.sort(key=lambda x: x['upload_date'], reverse=True)

        return photos
        
        # Sort by upload date (newest first)
        photos.sort(key=lambda x: x['upload_date'], reverse=True)
        st.session_state.all_photos = photos
        return photos
    
    def speak(self, text):
        """Convert text to speech"""
        st.session_state.assistant_response = text
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
        except:
            pass
    
    def listen(self):
        """Listen for voice commands"""
        try:
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            
            with microphone as source:
                st.info("🎤 Listening... Speak now!")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=10)
            
            command = recognizer.recognize_google(audio).lower()
            return command
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "unknown"
        except Exception as e:
            return f"error: {str(e)}"
    
    def extract_name_from_command(self, command):
        """Extract person name from voice command - FIXED LOGIC"""
        # Clean the command
        command = command.lower().strip()
        
        # Remove common phrases
        phrases_to_remove = [
            "show me", "show", "photo of", "picture of", "selfie of", 
            "photo", "picture", "selfie", "please", "can you", "give me"
        ]
        
        for phrase in phrases_to_remove:
            command = command.replace(phrase, "")
        
        command = command.strip()
        
        # If command is just a name, return it
        if command and len(command) > 1:
            return command
        return None
    
    def find_photo_by_name(self, person_name):
        """Find photo for a specific person - FIXED MATCHING"""
        if not person_name:
            return None
        
        # Clean the name
        person_name = person_name.lower().strip()
        
        for photo in st.session_state.all_photos:
            # Get filename without extension and clean it
            photo_name = os.path.splitext(photo['filename'])[0].lower().strip()
            
            # Direct match
            if photo_name == person_name:
                return photo
            
            # Partial match (if name contains the search term)
            if person_name in photo_name:
                return photo
            
            # Also check the capitalized name
            if person_name.capitalize() in photo['name']:
                return photo
        
        return None
    
    def process_command(self, command):
        """Process voice/text commands - FIXED LOGIC"""
        command = command.lower()
        
        # Debug: Show what command was received
        print(f"DEBUG: Received command: '{command}'")
        
        # Check for photo-related commands
        photo_keywords = ["show", "photo", "picture", "selfie", "see", "display", "view", "give"]
        has_photo_keyword = any(keyword in command for keyword in photo_keywords)
        
        if has_photo_keyword or any(word in command for word in ["Vlad", "Tatiana", "Yuri", "Kostya"]):
            # Extract name from command
            found_name = self.extract_name_from_command(command)
            
            # If no name found but command has common names, try to extract
            if not found_name:
                common_names = ["Vlad", "Yuri", "Viraj", "Tatiana", "Timur", "Ilya", "denis", "kostya","Sasha", "Vanya", "Stas","valera", "alina" ]
                for name in common_names:
                    if name in command:
                        found_name = name
                        break
            
            if found_name:
                print(f"DEBUG: Looking for photos of '{found_name}'")
                photo = self.find_photo_by_name(found_name)
                
                if photo:
                    st.session_state.current_image = photo
                    response = f"Here's {photo['name']}'s photo! 📸"
                    print(f"DEBUG: Found photo: {photo['filename']}")
                    return response, photo
                else:
                    # Show available names for debugging
                    available_names = [p['name'] for p in st.session_state.all_photos]
                    response = f"Sorry, no photo found for '{found_name}'. Available photos: {', '.join(available_names) if available_names else 'None'}"
                    print(f"DEBUG: No photo found. Available: {available_names}")
                    return response, None
            else:
                return "Please specify which person's photo you want. Try: 'show me photo of jack'", None
        
        elif "random" in command or "any" in command:
            if st.session_state.all_photos:
                random_photo = random.choice(st.session_state.all_photos)
                st.session_state.current_image = random_photo
                return f"Here's a random photo of {random_photo['name']}! 🎲", random_photo
            else:
                return "No photos available yet. Upload some photos first!", None
        
        elif "all photos" in command or "gallery" in command:
            if st.session_state.all_photos:
                st.session_state.current_image = None
                return f"Showing all {len(st.session_state.all_photos)} photos in the gallery! 🖼️", None
            else:
                return "No photos in the gallery yet. Upload some photos!", None
        
        elif "hello" in command or "hi" in command:
            return "Hello! I'm your voice assistant. Upload photos and say 'show me photo of [name]' to see them! 👋", None
        
        elif "help" in command:
            return "Say: 'show me photo of Jack' or 'show random photo' or 'show all photos'", None
        
        else:
            return "I can show you photos! Try: 'show me photo of Jack' or 'show random photo' 📷", None

def main():
    # Custom CSS
    local_css("static/style.css")
    
    # Add logo
    add_logo("logo.png", width=60)
    
    social_app = VoicePhotoSocial()
    
    # Header
    st.title("📸 Voice Photo Social")
    st.markdown("### Upload your photos and view them with voice commands! 🗣️")
    
    # Sidebar - Upload Section
    with st.sidebar:
        st.header("👤 Upload Your Photo")
        st.markdown("**Step 1:** Upload your photo with your name as filename")
        st.markdown("**Step 2:** Use voice commands to view photos")
        
        # File upload
        uploaded_file = st.file_uploader("Choose your photo", 
                                       type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
                                       key="upload_photo")
        
        if uploaded_file is not None:
            # Clean the filename - SIMPLIFIED
            original_name = uploaded_file.name
            # Remove file extension, clean the name, then add extension back
            name_only = os.path.splitext(original_name)[0]
            clean_name = name_only.lower().replace(" ", "_").strip()
            extension = os.path.splitext(original_name)[1].lower()
            final_filename = f"{clean_name}{extension}"
            
            # Save the file
            file_path = os.path.join("images", final_filename)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ Photo uploaded successfully!")
            st.info(f"**Your username:** {clean_name.capitalize()}")
            st.info("Now say: 'show me photo of [your name]'")
            
            # Refresh the photo list
            social_app.load_all_photos()
            st.rerun()
        
        st.markdown("---")
        st.header("🎯 Voice Commands")
        st.markdown("""
        **Try saying exactly:**
        - **"show me photo of jack"**
        - **"photo of emma"**
        - **"show jack"**
        - **"show random photo"** 
        - **"show all photos"**
        """)
        
        # Show current photos in sidebar
        st.header("📚 Available Photos")
        all_photos = st.session_state.all_photos
        if all_photos:
            for photo in all_photos:
                st.write(f"• **{photo['name']}** - {photo['filename']}")
        else:
            st.write("No photos yet. Upload one!")
        
        # Voice command button in sidebar
        if st.button("🎤 Start Voice Command", use_container_width=True, key="sidebar_voice"):
            with st.spinner("Listening... Speak now!"):
                command = social_app.listen()
                
                if command == "timeout":
                    st.error("⏰ No speech detected. Try again.")
                elif command == "unknown":
                    st.error("🔇 Could not understand speech. Try again.")
                elif command.startswith("error"):
                    st.error(f"❌ Error: {command}")
                else:
                    st.session_state.last_command = command
                    response, photo = social_app.process_command(command)
                    st.session_state.assistant_response = response
                    st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎤 Voice Control")
        
        # Display last command
        if st.session_state.last_command:
            st.markdown(f"**Your command:** `{st.session_state.last_command}`")
        
        # Voice command button
        if st.button("🎤 Start Voice Command", use_container_width=True, key="main_voice"):
            with st.spinner("Listening... Speak now!"):
                command = social_app.listen()
                
                if command == "timeout":
                    st.error("⏰ No speech detected. Try again.")
                elif command == "unknown":
                    st.error("🔇 Could not understand speech. Try again.")
                elif command.startswith("error"):
                    st.error(f"❌ Error: {command}")
                else:
                    st.session_state.last_command = command
                    response, photo = social_app.process_command(command)
                    st.session_state.assistant_response = response
                    st.rerun()
        
        # Text input as fallback
        st.subheader("💬 Type Command")
        text_command = st.text_input("Enter command (e.g., 'show photo of jack'):")
        if st.button("Submit Command", use_container_width=True) and text_command:
            st.session_state.last_command = text_command
            response, photo = social_app.process_command(text_command)
            st.session_state.assistant_response = response
            st.rerun()
        
        # Assistant response
        st.subheader("🤖 Assistant Response")
        st.info(st.session_state.assistant_response)
        
        # Text-to-speech button
        if st.button("🔊 Speak Response", use_container_width=True):
            social_app.speak(st.session_state.assistant_response)
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        col1a, col2a = st.columns(2)
        with col1a:
            if st.button("🔄 Refresh", use_container_width=True):
                social_app.load_all_photos()
                st.session_state.assistant_response = f"Refreshed! {len(st.session_state.all_photos)} photos available."
                st.rerun()
        with col2a:
            if st.button("🎲 Random", use_container_width=True):
                if st.session_state.all_photos:
                    random_photo = random.choice(st.session_state.all_photos)
                    st.session_state.current_image = random_photo
                    st.session_state.assistant_response = f"Showing random photo of {random_photo['name']}! 🎲"
                    st.rerun()
                else:
                    st.session_state.assistant_response = "No photos available yet!"
    
    with col2:
        st.subheader("🖼️ Photo Display")
        
        # If a specific photo is selected, show it large
        if st.session_state.current_image:
            photo = st.session_state.current_image
            try:
                image = Image.open(photo['path'])
                
                # Display photo
                st.image(image, caption=f"📷 {photo['name']}'s Photo", use_column_width=True)
                
                # Photo info
                st.markdown(f"""
                **Photo Info:**
                - 👤 **Name:** {photo['name']}
                - 📅 **Uploaded:** {photo['upload_date']}
                - 📏 **Size:** {photo['size'] // 1024} KB
                """)
                
                # Download button
                with open(photo['path'], "rb") as file:
                    st.download_button(
                        label="📥 Download This Photo",
                        data=file,
                        file_name=photo['filename'],
                        mime="image/jpeg",
                        use_container_width=True
                    )
                
                # Back to gallery button
                if st.button("← Back to Gallery", use_container_width=True):
                    st.session_state.current_image = None
                    st.session_state.assistant_response = "Showing all photos in gallery!"
                    st.rerun()
            
            except Exception as e:
                st.error(f"Error displaying photo: {str(e)}")
        
        else:
            # Show photo gallery
            all_photos = st.session_state.all_photos
            
            if all_photos:
                st.success(f"🎉 **{len(all_photos)} photos in gallery**")
                
                # Display photos in a grid
                cols = st.columns(3)
                for idx, photo in enumerate(all_photos):
                    with cols[idx % 3]:
                        try:
                            img = Image.open(photo['path'])
                            # Resize for thumbnail
                            img.thumbnail((200, 200))
                            
                            st.image(img, use_column_width=True)
                            st.caption(f"**{photo['name']}**")
                            
                            # Show button
                            if st.button(f"Show {photo['name']}", key=f"show_{idx}", use_container_width=True):
                                st.session_state.current_image = photo
                                st.session_state.assistant_response = f"Showing {photo['name']}'s photo! 📸"
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"Error loading {photo['name']}")
            else:
                st.info("👆 **No photos yet!** Upload your photo in the sidebar to get started!")
                st.markdown("""
                **How to start:**
                1. Go to the sidebar
                2. Upload your photo (name it with your name)
                3. Use voice commands to view photos
                4. Share with friends to build the gallery!
                """)
    
    # Footer
    st.markdown("---")
    st.markdown("### 🌐 Share this app with friends to build your photo gallery!")

if __name__ == "__main__":
    main()

