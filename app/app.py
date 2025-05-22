import os
import shutil
import subprocess
import uuid
import threading
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Max upload size: 25 MB
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
BASE_UPLOAD_FOLDER = 'uploads'
BASE_OUTPUT_FOLDER = 'output'
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BASE_OUTPUT_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )
from werkzeug.exceptions import RequestEntityTooLarge
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large. Max is 25 MB.'}), 413
    
def cleanup_session_folders(session_id):
    """Remove any existing session folders to ensure a clean slate."""
    upload_folder = os.path.join(BASE_UPLOAD_FOLDER, session_id)
    output_folder = os.path.join(BASE_OUTPUT_FOLDER, session_id)
    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

def schedule_cleanup(session_id, delay=900):
    """
    Schedule the cleanup of a session folder after a specified delay (default: 900 seconds = 15 minutes).
    """
    timer = threading.Timer(delay, lambda: cleanup_session_folders(session_id))
    timer.start()

def create_session_folders(session_id):
    """
    Clears previous session folders if they exist and creates new ones.
    This ensures that files from previous uploads won't mix with new ones.
    """
    cleanup_session_folders(session_id)
    upload_folder = os.path.join(BASE_UPLOAD_FOLDER, session_id)
    output_folder = os.path.join(BASE_OUTPUT_FOLDER, session_id)
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    return upload_folder, output_folder

def run_ocrmypdf(input_pdf, output_pdf):
    cmd = [
        'ocrmypdf',
        '--rotate-pages',
        '--deskew',
        '--output-type', 'pdfa',
        '--jobs', '4',
        input_pdf,
        output_pdf
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        if "PriorOcrFoundError" in result.stderr:
            raise ValueError("This file already contains selectable text and was skipped.")
        else:
            raise RuntimeError(f"OCRmyPDF failed: {result.stderr}")

@app.route('/')
def index():
    # Generate a new session id for each visitor.
    session_id = str(uuid.uuid4())
    return render_template('index.html', session_id=session_id)

@app.route('/upload/<session_id>', methods=['POST'])
def upload_files(session_id):
    # Create fresh session folders, clearing any previous data.
    upload_folder, output_folder = create_session_folders(session_id)

    if 'files' not in request.files:
        return jsonify({'error': 'No files were uploaded.'}), 400

    files = request.files.getlist('files')
    processed_files = []
    skipped_files = []

    for file in files:
        if file.filename == '':
            continue

        filename = secure_filename(file.filename)
        input_path = os.path.join(upload_folder, filename)
        output_path = os.path.join(output_folder, filename)
for file in files:
    if file.filename == '':
        continue

    if not allowed_file(file.filename):
        return jsonify({
            'error': f"Invalid file type: {file.filename}. Only PDF allowed."
        }), 400

    # Optionally also check MIME type:
    if file.mimetype not in ('application/pdf',):
        return jsonify({
            'error': f"Invalid MIME type for {file.filename}: {file.mimetype}"
        }), 400

    # … now save & process …

        file.save(input_path)

        try:
            run_ocrmypdf(input_path, output_path)
            processed_files.append(filename)
        except ValueError:
            skipped_files.append(filename)
        except Exception as e:
            # If there's an error, cleanup the session folders
            cleanup_session_folders(session_id)
            return jsonify({'error': f"Failed to process {filename}: {str(e)}"}), 500

    if not processed_files:
        schedule_cleanup(session_id)
        return jsonify({
            'error': 'All files were skipped because they already contain selectable text.',
            'skipped_files': skipped_files
        })

    # Create a zip file containing only the current upload's processed files.
    zip_filename = os.path.join(output_folder, 'processed_files.zip')
    subprocess.run(['zip', '-j', zip_filename] + [os.path.join(output_folder, f) for f in processed_files])

    # Schedule deletion of the session folders after 15 minutes.
    schedule_cleanup(session_id)

    return jsonify({
        'download_url': f'/download/{session_id}/processed_files.zip',
        'processed_files': processed_files,
        'skipped_files': skipped_files
    })

@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    file_path = os.path.join(BASE_OUTPUT_FOLDER, session_id, filename)
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
