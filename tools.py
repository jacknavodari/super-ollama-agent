import os
import subprocess
import shutil
import json
import datetime
from PIL import Image # Importăm Image din Pillow

def read_file(file_path):
    """
    Reads the content of a file and returns it as a string.
    Returns an error message if the file is not found or cannot be read.
    """
    try:
        # Expand user path (e.g., ~) and get absolute path
        abs_path = os.path.abspath(os.path.expanduser(file_path))
        
        if not os.path.exists(abs_path):
            return f"Error: File not found at '{abs_path}'."
        
        if not os.path.isfile(abs_path):
            return f"Error: Path '{abs_path}' is a directory, not a file."

        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"An unexpected error occurred while reading the file: {e}"

def execute_shell(command, cwd=None):
    """
    Executes a shell command and returns its stdout and stderr.
    WARNING: Executing arbitrary commands can be a security risk.
    """
    try:
        # For Windows, shell=True is needed to use cmd.exe or powershell.exe
        # capture_output=True captures stdout and stderr
        # text=True decodes stdout/stderr as text
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False, encoding='utf-8', cwd=cwd)
        
        output = {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
        
        if result.returncode != 0:
            return f"Error executing command (Return Code: {result.returncode}):\nSTDOUT: {output['stdout']}\nSTDERR: {output['stderr']}"
        
        return output['stdout'] if output['stdout'] else f"Command executed successfully (Return Code: {output['returncode']}), but produced no stdout."

    except Exception as e:
        return f"An unexpected error occurred while executing the command: {e}"

def write_file(file_path, content):
    """
    Writes content to a file. Creates directories if they don't exist.
    Overwrites the file if it already exists.
    """
    try:
        abs_path = os.path.abspath(os.path.expanduser(file_path))
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to '{abs_path}'."
    except Exception as e:
        return f"An unexpected error occurred while writing to the file: {e}"

def generate_dummy_ico(file_path, size=(16, 16), color=(0, 0, 0, 255)): # Default to solid black 16x16
    """
    Generates a simple .ico file with a single color.
    Requires Pillow (PIL) to be installed.
    """
    try:
        img = Image.new('RGBA', size, color)
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        img.save(file_path, format='ICO')
        return f"Successfully generated dummy ICO file at '{file_path}' ({size[0]}x{size[1]} pixels)."
    except Exception as e:
        return f"Error generating ICO file: {e}"

def detect_app_creation_request(user_input):
    """
    Detects if the user wants to create an application.
    """
    app_creation_keywords = [
        'app', 'application', 'program', 'software', 'tool', 'utility',
        'website', 'site', 'webapp',
        'game',
        'script',
        'bot'
    ]
    
    app_creation_patterns = [
        ('create', 'app'),
        ('build', 'app'),
        ('make', 'app'),
        ('develop', 'app'),
        ('create', 'application'),
        ('build', 'application'),
        ('make', 'application'),
        ('develop', 'application'),
        ('create', 'website'),
        ('build', 'website'),
        ('make', 'website'),
        ('develop', 'website'),
        ('create', 'game'),
        ('build', 'game'),
        ('make', 'game'),
        ('develop', 'game'),
    ]

    user_input_lower = user_input.lower()

    for keyword in app_creation_keywords:
        if keyword in user_input_lower:
            # check if it's a part of a word
            if f' {keyword} ' in f' {user_input_lower} ' or user_input_lower.startswith(f'{keyword} ') or user_input_lower.endswith(f' {keyword}'):
                 return True

    words = user_input_lower.split()
    for pattern in app_creation_patterns:
        if pattern[0] in words and pattern[1] in words:
            return True

    return False


def create_electron_schedule_app(app_name, child_name="Nume Copil", class_name="Clasa Pregătitoare 2025-2026"):
    """
    Creates a complete Electron application for a schedule/timetable app.
    Similar to the electron-orar-app structure with schedule view, events, and dark mode.
    """
    try:
        import json

        # Define the app structure with all necessary files
        app_files = {
            "package.json": f'''{{
  "name": "{app_name.lower().replace(" ", "-")}",
  "version": "1.0.0",
  "description": "Electron app for school schedule",
  "main": "main.js",
  "scripts": {{
    "start": "electron .",
    "build": "electron-builder --win --x64",
    "dist": "npm run build",
    "pack": "electron-builder --dir",
    "publish": "electron-builder -p always"
  }},
  "keywords": [
    "electron",
    "school",
    "schedule",
    "timetable"
  ],
  "author": "{app_name} App",
  "license": "MIT",
  "build": {{
    "appId": "com.{app_name.lower().replace(" ", "")}.app",
    "productName": "{app_name}",
    "directories": {{
      "output": "release"
    }},
    "win": {{
      "target": "nsis",
      "icon": "icon.ico"
    }},
    "mac": {{
      "target": "dmg",
      "icon": "icon.icns"
    }},
    "linux": {{
      "target": "AppImage",
      "icon": "icon.png"
    }}
  }},
  "devDependencies": {{
    "electron": "^28.0.0",
    "electron-builder": "^24.6.0"
  }},
  "dependencies": {{
    "electron-is-dev": "^2.0.0"
  }}
}}''',
            "main.js": '''const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'), // Optional: Add an icon
    resizable: true,
    backgroundColor: '#f0f4f8'
  });

  // Load the index.html file
  mainWindow.loadFile('index.html');

  // Open the DevTools if in development mode
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Create a simple menu
  const menuTemplate = [
    {
      label: 'File',
      submenu: [
        { role: 'reload' },
        { role: 'toggledevtools' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'zoomin' },
        { role: 'zoomout' },
        { role: 'resetzoom' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows are closed, except on macOS.
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
''',
            "preload.js": '''const { contextBridge } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Add any API functions here if needed in the future
});
''',
            "index.html": f'''<!DOCTYPE html>
<html lang="ro">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title id="page-title">{app_name} - {child_name}</title>
    <style>
        :root {{
            --primary: #667eea;
            --secondary: #764ba2;
            --accent: #ff6b6b;
            --text: #2d3436;
            --bg: #f0f4f8;
            --card-bg: #ffffff;
        }}

        body {{
            font-family: 'Segoe UI', sans-serif;
            background: var(--bg);
            margin: 0;
            padding: 0;
            color: var(--text);
            -webkit-tap-highlight-color: transparent;
        }}

        .app-container {{
            max-width: 600px;
            margin: 0 auto;
            padding-bottom: 80px;
        }}

        header {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 20px;
            border-radius: 0 0 25px 25px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}

        h1 {{
            margin: 0;
            font-size: 1.5rem;
        }}

        p {{
            margin: 5px 0 0;
            opacity: 0.9;
            font-size: 0.9rem;
        }}

        .view-toggle {{
            display: flex;
            justify-content: center;
            padding: 10px;
            gap: 10px;
            background: var(--bg);
        }}

        .view-btn {{
            background: white;
            border: none;
            padding: 8px 15px;
            border-radius: 12px;
            font-weight: bold;
            color: #a0a0a0;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            cursor: pointer;
        }}

        .view-btn.active {{
            background: var(--primary);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.4);
        }}

        .day-tabs {{
            display: flex;
            justify-content: space-between;
            padding: 15px 10px;
            position: sticky;
            top: 0;
            background: var(--bg);
            z-index: 100;
        }}

        .day-tab {{
            background: white;
            border: none;
            padding: 10px;
            border-radius: 12px;
            font-weight: bold;
            color: #a0a0a0;
            width: 18%;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            cursor: pointer;
        }}

        .day-tab.active {{
            background: var(--primary);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.4);
        }}

        .schedule-list {{
            padding: 10px 20px;
        }}

        .class-card {{
            background: var(--card-bg);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            border-left: 5px solid transparent;
            transition: transform 0.2s;
        }}

        .class-card.active {{
            border-left-color: var(--accent);
            background: #fff5f5;
            transform: scale(1.02);
        }}

        .time-slot {{
            font-weight: bold;
            color: var(--primary);
            font-size: 0.9rem;
            width: 80px;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
        }}

        .time-slot span:last-child {{
            font-size: 0.75rem;
            color: #888;
            font-weight: normal;
        }}

        .subject-info {{
            flex-grow: 1;
            padding-left: 15px;
            border-left: 1px solid #eee;
        }}

        .subject-name {{
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 4px;
        }}

        .subject-type {{
            font-size: 0.8rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .status-bar {{
            background: var(--accent);
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 0.9rem;
            margin: 10px 20px;
            border-radius: 10px;
            display: none;
            /* Hidden by default */
            animation: pulse 2s infinite;
        }}

        .status-bar.active-class {{
            background: var(--accent);
        }}

        .status-bar.next-class {{
            background: var(--primary);
        }}

        @keyframes pulse {{
            0% {{
                opacity: 1;
            }}

            50% {{
                opacity: 0.85;
            }}

            100% {{
                opacity: 1;
            }}
        }}

        .event-form {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 15px;
            padding: 20px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
            z-index: 1001;
            display: none;
            box-sizing: border-box;
        }}

        .form-group {{
            margin-bottom: 15px;
        }}

        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }}

        .form-group input,
        .form-group textarea,
        .form-group select {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
        }}

        .form-group textarea {{
            height: 80px;
            resize: vertical;
        }}

        .form-actions {{
            display: flex;
            gap: 10px;
        }}

        .form-actions button {{
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }}

        .save-event {{
            background: var(--primary);
            color: white;
            flex: 1;
        }}

        .cancel-event {{
            background: #f0f0f0;
            color: #666;
            flex: 1;
        }}

        .teachers-section {{
            padding: 20px;
        }}

        .teacher-mini {{
            background: white;
            padding: 10px 15px;
            border-radius: 10px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
        }}

        .add-event-btn {{
            display: block;
            width: 100%;
            padding: 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 15px;
            text-align: center;
            font-size: 1rem;
        }}

        .event-list {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}

        .event-item {{
            background: #e8f5e8;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }}

        .event-details {{
            flex-grow: 1;
        }}

        .event-time {{
            font-weight: bold;
            color: var(--primary);
        }}

        .event-title {{
            display: block;
            font-weight: 600;
        }}

        .event-description {{
            font-size: 0.8rem;
            color: #666;
            margin-top: 2px;
        }}

        .event-actions-container {{
            display: flex;
            gap: 5px;
        }}

        .delete-event {{
            background: #f44336;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 8px;
            cursor: pointer;
            font-size: 0.8rem;
        }}

        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            display: none;
        }}

        /* Dark Mode */
        body.dark-mode {{
            --primary: #5c6bc0;
            --secondary: #3f51b5;
            --accent: #ff7043;
            --text: #e0e0e0;
            --bg: #121212;
            --card-bg: #1e1e1e;
        }}

        .dark-mode .view-btn {{
            background: #2d2d2d;
            color: #b0b0b0;
        }}

        .dark-mode .day-tab {{
            background: #2d2d2d;
            color: #b0b0b0;
        }}

        .dark-mode .class-card {{
            background: #2d2d2d;
            color: #e0e0e0;
        }}

        .dark-mode .event-item {{
            background: #2d2d2d;
            color: #e0e0e0;
        }}

        .dark-mode .add-event-btn {{
            background: #43a047;
        }}

        .dark-mode .event-form {{
            background: #2d2d2d;
            color: #e0e0e0;
        }}

        .dark-mode .teacher-mini {{
            background: #2d2d2d;
            color: #e0e0e0;
        }}

        .dark-mode input,
        .dark-mode select,
        .dark-mode textarea {{
            background: #333;
            color: #e0e0e0;
            border: 1px solid #555;
        }}

        .toast {{
            visibility: hidden;
            min-width: 250px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 25px;
            padding: 16px;
            position: fixed;
            z-index: 2000;
            left: 50%;
            bottom: 30px;
            transform: translateX(-50%);
            font-size: 17px;
            opacity: 0;
            transition: opacity 0.3s, bottom 0.3s;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        }}

        .toast.show {{
            visibility: visible;
            opacity: 1;
            bottom: 50px;
        }}
    </style>
</head>

<body>
    <div class="app-container">
        <header>
            <h1 id="main-title">{app_name} <span id="child-name">{child_name}</span></h1>
            <p>{class_name}</p>
            <div style="text-align: right; margin-top: 10px;">
                <button id="name-edit-btn" onclick="editChildName()"
                    style="background: rgba(255,255,255,0.2); border: 1px solid white; border-radius: 20px; padding: 5px 10px; color: white; cursor: pointer; margin-right: 10px;">✏️</button>
                <button id="dark-mode-toggle" onclick="toggleDarkMode()"
                    style="background: rgba(255,255,255,0.2); border: 1px solid white; border-radius: 20px; padding: 5px 10px; color: white; cursor: pointer;">🌙
                    Mod Întunecat</button>
            </div>
        </header>

        <div id="status-bar" class="status-bar"></div>

        <div class="view-toggle">
            <button id="schedule-view-btn" class="view-btn active" onclick="switchView('schedule')">Orar</button>
        </div>

        <nav class="day-tabs" id="day-tabs">
            <button class="day-tab" onclick="selectDay(0)">L</button>
            <button class="day-tab" onclick="selectDay(1)">M</button>
            <button class="day-tab" onclick="selectDay(2)">M</button>
            <button class="day-tab" onclick="selectDay(3)">J</button>
            <button class="day-tab" onclick="selectDay(4)">V</button>
        </nav>

        <div id="schedule-list" class="schedule-list">
            <!-- Content injected by JS -->
        </div>

        <div class="modal-overlay" id="modal-overlay"></div>

        <div id="event-form" class="event-form">
            <div class="form-group">
                <label for="event-title">Titlu Eveniment</label>
                <input type="text" id="event-title" placeholder="Introdu titlul evenimentului">
            </div>
            <div class="form-group">
                <label for="event-date">Dată</label>
                <input type="date" id="event-date">
            </div>
            <div class="form-group">
                <label for="event-time">Oră</label>
                <select id="event-time">
                    <option value="08:00">08:00</option>
                    <option value="08:30">08:30</option>
                    <option value="09:00">09:00</option>
                    <option value="09:30">09:30</option>
                    <option value="10:00">10:00</option>
                    <option value="10:30">10:30</option>
                    <option value="11:00">11:00</option>
                    <option value="11:30">11:30</option>
                    <option value="12:00">12:00</option>
                    <option value="12:30">12:30</option>
                    <option value="13:00">13:00</option>
                    <option value="13:30">13:30</option>
                    <option value="14:00">14:00</option>
                    <option value="14:30">14:30</option>
                    <option value="15:00">15:00</option>
                    <option value="15:30">15:30</option>
                    <option value="16:00">16:00</option>
                    <option value="16:30">16:30</option>
                    <option value="17:00">17:00</option>
                    <option value="17:30">17:30</option>
                    <option value="18:00">18:00</option>
                </select>
            </div>
            <div class="form-group">
                <label for="event-description">Descriere</label>
                <textarea id="event-description" placeholder="Descriere opțională"></textarea>
            </div>
            <div class="form-actions">
                <button class="save-event" onclick="saveEvent()">Salvează</button>
                <button class="cancel-event" onclick="hideEventForm()">Anulează</button>
            </div>
        </div>

        <!-- Edit Name Modal -->
        <div id="name-modal" class="event-form" style="height: auto;">
            <h3 style="margin-top: 0;">Modificare Nume</h3>
            <div class="form-group">
                <label for="child-name-input">Nume Copil</label>
                <input type="text" id="child-name-input" placeholder="Introduceți numele">
            </div>
            <div class="form-actions">
                <button class="save-event" onclick="saveChildName()">Salvează</button>
                <button class="cancel-event" onclick="closeNameModal()">Anulează</button>
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <div id="delete-modal" class="event-form" style="height: auto;">
            <h3 style="margin-top: 0;">Confirmare Ștergere</h3>
            <p>Sunteți sigur că doriți să ștergeți acest eveniment?</p>
            <div class="form-actions">
                <button class="delete-event" style="width: 100%; justify-content: center;" onclick="confirmDeleteEvent()">Da, Șterge</button>
                <button class="cancel-event" onclick="closeDeleteModal()">Nu, Anulează</button>
            </div>
        </div>

        <div class="teachers-section">
            <h3 style="margin-bottom: 15px; color: var(--secondary);">Cadre Didactice</h3>
            <div id="teachers-list"></div>
        </div>
    </div>

    <script>
        const schedule = [
            // Luni (0)
            [
                {{ start: "08:00", end: "08:45", subject: "Religie", type: "Educație" }},
                {{ start: "08:55", end: "09:40", subject: "Comunicare în lb. română", type: "CLR" }},
                {{ start: "09:50", end: "10:35", subject: "Matematică și expl. mediului", type: "MEM" }},
                {{ start: "10:45", end: "11:25", subject: "Muzică și mișcare", type: "MM" }}
            ],
            // Marti (1)
            [
                {{ start: "08:00", end: "08:45", subject: "Matematică și expl. mediului", type: "MEM" }},
                {{ start: "08:55", end: "09:40", subject: "Comunicare în lb. română", type: "CLR" }},
                {{ start: "09:50", end: "10:35", subject: "Dezvoltare personală", type: "DP" }},
                {{ start: "10:45", end: "11:25", subject: "Ed. Fizică", type: "Sport" }}
            ],
            // Miercuri (2)
            [
                {{ start: "08:00", end: "08:45", subject: "Comunicare în lb. română", type: "CLR" }},
                {{ start: "08:55", end: "09:40", subject: "Matematică și expl. mediului", type: "MEM" }},
                {{ start: "09:50", end: "10:35", subject: "Muzică și mișcare", type: "MM" }},
                {{ start: "10:45", end: "11:25", subject: "AVAP", type: "Arte" }}
            ],
            // Joi (3)
            [
                {{ start: "08:00", end: "08:45", subject: "Matematică și expl. mediului", type: "MEM" }},
                {{ start: "08:55", end: "09:40", subject: "Comunicare în lb. română", type: "CLR" }},
                {{ start: "09:50", end: "10:35", subject: "Ed. Fizică", type: "Sport" }},
                {{ start: "10:45", end: "11:25", subject: "Dezvoltare personală", type: "DP" }}
            ],
            // Vineri (4)
            [
                {{ start: "08:00", end: "08:45", subject: "L.B. Engleză", type: "L. Mod" }},
                {{ start: "08:55", end: "09:40", subject: "Comunicare în lb. română", type: "CLR" }},
                {{ start: "09:50", end: "10:35", subject: "AVAP", type: "Arte" }}
            ]
        ];

        const teachers = [
            {{ name: "Giurgea Cristiana", role: "Învățător" }},
            {{ name: "Manea Adrian", role: "Ed. Fizică" }},
            {{ name: "Vlad Ștefania", role: "Lb. Engleză" }},
            {{ name: "Radu Stanciu", role: "Religie" }}
        ];

        // Calendar state
        let events = JSON.parse(localStorage.getItem('events')) || [];

        function renderTeachers() {{
            const container = document.getElementById('teachers-list');
            container.innerHTML = teachers.map(t => `
                <div class="teacher-mini">
                    <span style="font-weight:600">${{t.name}}</span>
                    <span style="color:#666">${{t.role}}</span>
                </div>
            `).join('');
        }}

        function selectDay(dayIndex) {{
            // Update Tabs
            document.querySelectorAll('.day-tab').forEach((tab, idx) => {{
                if (idx === dayIndex) tab.classList.add('active');
                else tab.classList.remove('active');
            }});

            // Render Schedule
            const list = document.getElementById('schedule-list');
            const daySchedule = schedule[dayIndex];

            if (!daySchedule) {{
                list.innerHTML = '<div style="text-align:center; padding:20px; color:#888">Liber! 🎉</div>';
                return;
            }}

            // Build the schedule HTML
            let scheduleHTML = daySchedule.map(cls => {{
                const isActive = isTimeActive(cls.start, cls.end, dayIndex);
                return `
                <div class="class-card ${{isActive ? 'active' : ''}}">
                    <div class="time-slot">
                        <span>${{cls.start}}</span>
                        <span>${{cls.end}}</span>
                    </div>
                    <div class="subject-info">
                        <div class="subject-name">${{cls.subject}}</div>
                        <div class="subject-type">${{cls.type}}</div>
                    </div>
                </div>
                `;
            }}).join('');

            // Calculate the actual date for the selected day of the current week
            const today = new Date();
            const dayOfWeek = today.getDay();
            const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
            const mondayOfCurrentWeek = new Date(today);
            mondayOfCurrentWeek.setDate(today.getDate() - daysToSubtract);

            const selectedDate = new Date(mondayOfCurrentWeek);
            selectedDate.setDate(mondayOfCurrentWeek.getDate() + dayIndex);
            const selectedDateFormatted = formatDate(selectedDate);

            // Add events for the selected day
            const dayEvents = events.filter(e => e.date === selectedDateFormatted);

            if (dayEvents.length > 0) {{
                scheduleHTML += '<div class="event-list">';
                dayEvents.forEach(event => {{
                    scheduleHTML += `
                    <div class="event-item" data-event-id="${{event.id}}">
                        <div class="event-details">
                            <span class="event-time">${{event.time}}</span>
                            <span class="event-title">${{event.title}}</span>
                            ${{event.description ? `<span class="event-description">${{event.description}}</span>` : ''}}
                        </div>
                        <div class="event-actions-container">
                            <button class="delete-event" data-event-id="${{event.id}}">Șterge</button>
                        </div>
                    </div>
                    `;
                }});
                scheduleHTML += '</div>';
            }}

            // Add "Add Event" button for the selected day
            scheduleHTML += `<button class="add-event-btn" id="add-event-schedule-btn" onclick="showEventForm('${{selectedDateFormatted}}')">Adaugă Eveniment pentru ${{getDayName(dayIndex)}}</button>`;

            list.innerHTML = scheduleHTML;

            list.onclick = function (e) {{
                if (e.target && e.target.classList.contains('delete-event')) {{
                    const eventId = e.target.getAttribute('data-event-id');
                    deleteEvent(eventId);
                    e.preventDefault();
                    return false;
                }}
            }};
        }}

        function getDayName(dayIndex) {{
            const dayNames = ['Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri'];
            return dayNames[dayIndex];
        }}

        function formatDate(date) {{
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${{year}}-${{month}}-${{day}}`;
        }}

        let eventIdToDelete = null;

        function showDeleteModal(id) {{
            eventIdToDelete = id;
            document.getElementById('modal-overlay').style.display = 'block';
            document.getElementById('delete-modal').style.display = 'block';
        }}

        function closeDeleteModal() {{
            eventIdToDelete = null;
            document.getElementById('modal-overlay').style.display = 'none';
            document.getElementById('delete-modal').style.display = 'none';
        }}

        function confirmDeleteEvent() {{
            if (eventIdToDelete) {{
                const numericId = Number(eventIdToDelete);
                events = events.filter(e => Number(e.id) !== numericId);
                localStorage.setItem('events', JSON.stringify(events));

                const currentDayIndex = Array.from(document.querySelectorAll('.day-tab')).findIndex(tab => tab.classList.contains('active'));
                if (currentDayIndex >= 0 && currentDayIndex <= 4) {{
                    selectDay(currentDayIndex);
                }}
            }}
            closeDeleteModal();
        }}

        function deleteEvent(eventId) {{
            showDeleteModal(eventId);
        }}

        function isTimeActive(start, end, dayIndex) {{
            const now = new Date();
            const currentDay = now.getDay() - 1;
            if (currentDay !== dayIndex) return false;

            const [h1, m1] = start.split(':').map(Number);
            const [h2, m2] = end.split(':').map(Number);

            const startTime = h1 * 60 + m1;
            const endTime = h2 * 60 + m2;
            const curTime = now.getHours() * 60 + now.getMinutes();

            return curTime >= startTime && curTime < endTime;
        }}

        function updateStatus() {{
            const now = new Date();
            const day = now.getDay() - 1;
            const statusBar = document.getElementById('status-bar');

            statusBar.classList.remove('active-class', 'next-class');

            if (day >= 0 && day < 5) {{
                const daySchedule = schedule[day];
                const curTime = now.getHours() * 60 + now.getMinutes();

                let activeClass = null;
                let nextClass = null;

                for (let cls of daySchedule) {{
                    const [h1, m1] = cls.start.split(':').map(Number);
                    const [h2, m2] = cls.end.split(':').map(Number);
                    const start = h1 * 60 + m1;
                    const end = h2 * 60 + m2;

                    if (curTime >= start && curTime < end) {{
                        activeClass = cls;
                    }} else if (curTime < start && !nextClass) {{
                        nextClass = cls;
                    }}
                }}

                if (activeClass) {{
                    statusBar.style.display = 'block';
                    statusBar.innerHTML = `Acum: ${{activeClass.subject}}`;
                    statusBar.classList.add('active-class');
                }} else if (nextClass) {{
                    statusBar.style.display = 'block';
                    statusBar.innerHTML = `Urmează: ${{nextClass.subject}} la ${{nextClass.start}}`;
                    statusBar.classList.add('next-class');
                }} else {{
                    statusBar.style.display = 'none';
                }}
            }}
        }}

        function switchView(view) {{
            document.getElementById('schedule-list').style.display = 'block';
            document.getElementById('day-tabs').style.display = 'flex';
            document.getElementById('schedule-view-btn').classList.add('active');
        }}

        function showEventForm(dateStr = null) {{
            document.getElementById('modal-overlay').style.display = 'block';
            document.getElementById('event-form').style.display = 'block';

            const addEventScheduleBtn = document.getElementById('add-event-schedule-btn');
            if (addEventScheduleBtn) {{
                addEventScheduleBtn.style.display = 'none';
            }}

            if (dateStr) {{
                document.getElementById('event-date').value = dateStr;
            }} else {{
                const today = new Date();
                const todayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
                document.getElementById('event-date').value = formatDate(todayDate);
            }}
        }}

        function hideEventForm() {{
            document.getElementById('modal-overlay').style.display = 'none';
            document.getElementById('event-form').style.display = 'none';

            const addEventScheduleBtn = document.getElementById('add-event-schedule-btn');
            if (addEventScheduleBtn) {{
                addEventScheduleBtn.style.display = 'block';
            }}

            document.getElementById('event-title').value = '';
            document.getElementById('event-description').value = '';
        }}

        function showToast(message) {{
            let toast = document.getElementById("toast");
            if (!toast) {{
                toast = document.createElement("div");
                toast.id = "toast";
                toast.className = "toast";
                document.body.appendChild(toast);
            }}
            toast.textContent = message;
            toast.className = "toast show";
            setTimeout(function () {{ toast.className = toast.className.replace("show", ""); }}, 3000);
        }}

        function saveEvent() {{
            const title = document.getElementById('event-title').value.trim();
            const date = document.getElementById('event-date').value;
            const time = document.getElementById('event-time').value;
            const description = document.getElementById('event-description').value.trim();

            if (!title) {{
                showToast('Vă rugăm să introduceți un titlu pentru eveniment');
                return;
            }}

            if (!date) {{
                showToast('Vă rugăm să selectați o dată');
                return;
            }}

            if (!time) {{
                showToast('Vă rugăm să selectați o oră');
                return;
            }}

            const event = {{
                id: Date.now(),
                title,
                date,
                time,
                description,
                createdAt: new Date().toISOString()
            }};

            events.push(event);
            localStorage.setItem('events', JSON.stringify(events));

            const today = new Date().getDay() - 1;
            if (today >= 0 && today <= 4) {{
                selectDay(today);
            }}

            hideEventForm();
            showToast('Evenimentul a fost adăugat!');
        }}

        function toggleDarkMode() {{
            const body = document.body;
            const toggleButton = document.getElementById('dark-mode-toggle');

            if (body.classList.contains('dark-mode')) {{
                body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
                toggleButton.innerHTML = '🌙 Mod Întunecat';
            }} else {{
                body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
                toggleButton.innerHTML = '☀️ Mod Luminos';
            }}
        }}

        function editChildName() {{
            const currentName = localStorage.getItem('childName') || '{child_name}';
            document.getElementById('child-name-input').value = currentName;
            document.getElementById('modal-overlay').style.display = 'block';
            document.getElementById('name-modal').style.display = 'block';
        }}

        function closeNameModal() {{
            document.getElementById('modal-overlay').style.display = 'none';
            document.getElementById('name-modal').style.display = 'none';
        }}

        function saveChildName() {{
            const newName = document.getElementById('child-name-input').value.trim();
            if (newName) {{
                localStorage.setItem('childName', newName);
                const childNameElement = document.getElementById('child-name');
                if (childNameElement) {{
                    childNameElement.textContent = newName;
                }}
                const pageTitleElement = document.getElementById('page-title');
                if (pageTitleElement) {{
                    pageTitleElement.textContent = `{app_name} ${{newName}}`;
                }}
                document.title = `{app_name} ${{newName}}`;
            }}
            closeNameModal();
        }}

        // Init
        function initDarkMode() {{
            const isDarkMode = localStorage.getItem('darkMode') === 'true';
            const toggleButton = document.getElementById('dark-mode-toggle');

            if (isDarkMode) {{
                document.body.classList.add('dark-mode');
                if (toggleButton) {{
                    toggleButton.innerHTML = '☀️ Mod Luminos';
                }}
            }}
        }}
    </script>
</body>

</html>
'''
        }

        # Use the existing create_app_structure tool to create the files
        creation_result = create_app_structure(app_name, app_files, location="current", validate_code=False)
        print(f"Agent: {creation_result}")

        # After creating the files, change into the app directory and run npm install
        original_cwd = os.getcwd()
        try:
            app_path = os.path.join(original_cwd, app_name)
            os.chdir(app_path)
            
            # Check if npm is available
            check_npm = execute_shell("npm -v")
            if "Error" in check_npm or "not recognized" in check_npm:
                return f"Error: npm is not found. Please ensure Node.js and npm are installed and in your PATH. Details: {check_npm}"

            # Install dependencies
            print(f"Agent: Running 'npm install' in '{app_name}'... This may take a few minutes.")
            install_result = execute_shell("npm install")
            print(f"Agent: npm install output:\n{install_result}")
            if "Error" in install_result:
                return f"Error installing dependencies for '{app_name}': {install_result}"

            return (f"Successfully created and set up Electron schedule application '{app_name}'.\n"
                    f"To run the app: cd {app_name} && npm start")

        finally:
            os.chdir(original_cwd) # Change back to the original directory

    except Exception as e:
        return f"An unexpected error occurred while creating Electron schedule app: {e}"
