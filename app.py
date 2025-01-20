from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for
import os
import subprocess

app = Flask(__name__)

# Path to the directory containing media files
MEDIA_FOLDER = "media"
TEMP_FOLDER = "temp"
os.makedirs(MEDIA_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

@app.route('/')
def home():
    def get_file_structure(folder):
        file_structure = []
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):
                file_structure.append({"name": item, "type": "folder"})
            elif item.endswith(('.mp4', '.mkv')):
                file_structure.append({"name": item, "type": "file"})
        return file_structure

    file_structure = get_file_structure(MEDIA_FOLDER)
    return render_template('file_manager.html', file_structure=file_structure)

@app.route('/media/<path:filename>')
def media(filename):
    # Check if the file is an MKV or MP4 and serve with appropriate MIME type
    if filename.endswith('.mkv'):
        return send_from_directory(MEDIA_FOLDER, filename, mimetype='video/x-matroska')
    else:
        return send_from_directory(MEDIA_FOLDER, filename)

@app.route('/subtitles/<path:filename>')
def extract_subtitles(filename):
    video_path = os.path.join(MEDIA_FOLDER, filename)
    subtitle_path = os.path.join(TEMP_FOLDER, f"{filename}.vtt")

    try:
        # Extract subtitles using ffmpeg for both .mkv and .mp4
        if filename.endswith('.mkv'):
            subprocess.run([
                "ffmpeg", "-y", "-i", video_path, "-map", "0:s:0", subtitle_path
            ], check=True)
        else:
            subprocess.run([
                "ffmpeg", "-y", "-i", video_path, "-map", "0:s:0", subtitle_path
            ], check=True)

        return send_from_directory(TEMP_FOLDER, f"{filename}.vtt")
    except subprocess.CalledProcessError:
        return jsonify({"error": "No subtitles found in the video."}), 404

@app.route('/view/<path:filepath>')
def view_file(filepath):
    if os.path.isdir(os.path.join(MEDIA_FOLDER, filepath)):
        # If it's a folder, show its contents
        def get_file_structure(folder):
            file_structure = []
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if os.path.isdir(item_path):
                    file_structure.append({"name": item, "type": "folder"})
                elif item.endswith(('.mp4', '.mkv')):
                    file_structure.append({"name": item, "type": "file"})
            return file_structure

        folder_structure = get_file_structure(os.path.join(MEDIA_FOLDER, filepath))
        return render_template('file_manager.html', file_structure=folder_structure, parent=filepath)
    else:
        # If it's a file, redirect to its media endpoint
        return redirect(url_for('media', filename=filepath))

if __name__ == '__main__':
    # Bind to all IP addresses on port 72727
    app.run(host='0.0.0.0', port=72727)
