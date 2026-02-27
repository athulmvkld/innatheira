from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# ==========================================
# STATE: Current list of persons
# ==========================================
DEFAULT_PERSONS = [
    "athul", "shinil", "monu", "pintu", 
    "unnikuttan", "manikuttettan", "achu", "amar", "nikhil"
]
person_list = DEFAULT_PERSONS.copy()

# The HTML, CSS, and JS frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lucky Spin Wheel</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { box-sizing: border-box; }
        body { 
            display: flex; margin: 0; min-height: 100vh;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); 
            font-family: 'Poppins', sans-serif; color: #fff;
        }
        
        .main-content {
            flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
            padding: 20px; overflow: hidden;
        }
        
        .sidebar {
            width: 350px; background: rgba(0, 0, 0, 0.3); backdrop-filter: blur(10px);
            border-left: 1px solid rgba(255,255,255,0.1); padding: 25px;
            display: flex; flex-direction: column; height: 100vh; overflow-y: auto;
        }

        h1 { 
            margin-top: 0; font-weight: 800; font-size: 2.5rem; letter-spacing: 1px; 
            text-transform: uppercase; text-shadow: 0 4px 10px rgba(0,0,0,0.4); 
            text-align: center; margin-bottom: 20px;
        }
        
        /* Wheel Styles */
        .wheel-container { position: relative; width: 400px; height: 400px; margin: 20px 0; }
        
        .pointer { 
            position: absolute; top: -15px; left: 50%; transform: translateX(-50%); 
            width: 0; height: 0; border-left: 20px solid transparent; border-right: 20px solid transparent; 
            border-top: 40px solid #ff4757; z-index: 10; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5)); 
        }
        
        .wheel { 
            width: 100%; height: 100%; border-radius: 50%; box-sizing: border-box; 
            transition: transform 30s cubic-bezier(0.1, 0.9, 0.2, 1); position: relative; 
            overflow: hidden; 
            box-shadow: 0 0 0 8px #ffffff11, 0 10px 30px rgba(0,0,0,0.5); 
        }
        
        .center-dot {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 45px; height: 45px; background: #fff; border-radius: 50%; z-index: 5;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3); border: 4px solid #2c5364;
        }
        
        .label { 
            position: absolute; top: 50%; left: 50%; transform-origin: 0 0; 
            font-weight: 600; text-shadow: 1px 1px 4px rgba(0,0,0,0.5); 
            font-size: 18px; pointer-events: none; white-space: nowrap;
        }
        
        .spin-btn { 
            margin-top: 30px; padding: 15px 50px; font-size: 22px; font-weight: 800; color: #fff; 
            background: linear-gradient(45deg, #1dd1a1, #10ac84); border: none; border-radius: 50px; 
            cursor: pointer; box-shadow: 0 8px 15px rgba(29, 209, 161, 0.4); transition: all 0.3s; 
            text-transform: uppercase; letter-spacing: 2px;
        }
        .spin-btn:hover:not(:disabled) { 
            background: linear-gradient(45deg, #10ac84, #1dd1a1); 
            box-shadow: 0 12px 20px rgba(29, 209, 161, 0.6); transform: translateY(-2px); 
        }
        .spin-btn:active:not(:disabled) { transform: translateY(2px); box-shadow: 0 4px 10px rgba(29, 209, 161, 0.4); }
        .spin-btn:disabled { background: #7f8fa6; cursor: not-allowed; box-shadow: none; opacity: 0.6; }
        
        #winner { 
            margin-top: 25px; font-size: 30px; font-weight: 800; min-height: 45px; 
            text-shadow: 0 2px 5px rgba(0,0,0,0.4); text-align: center; color: #feca57;
            opacity: 0; transition: opacity 0.5s;
        }
        #winner.show { opacity: 1; animation: pop 0.6s cubic-bezier(0.17, 0.89, 0.32, 1.49); }
        
        /* Sidebar Styles */
        .sidebar h2 { margin-top: 0; font-size: 1.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3); border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 15px;}
        
        .add-form { display: flex; margin-bottom: 20px; gap: 10px; }
        .add-form input { 
            flex: 1; padding: 10px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); 
            background: rgba(255,255,255,0.1); color: white; font-family: 'Poppins', sans-serif;
            outline: none;
        }
        .add-form input::placeholder { color: rgba(255,255,255,0.6); }
        .add-form button { 
            padding: 10px 15px; border-radius: 8px; border: none; background: #3498db; 
            color: white; font-weight: bold; cursor: pointer; transition: 0.2s;
        }
        .add-form button:hover { background: #2980b9; }

        .person-list { display: flex; flex-direction: column; gap: 10px; flex: 1; overflow-y: auto; padding-right: 5px; }
        .person-list::-webkit-scrollbar { width: 6px; }
        .person-list::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 4px; }
        .person-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
        
        .person-item {
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(255,255,255,0.05); padding: 12px 15px; border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05); transition: 0.2s;
        }
        .person-item:hover { background: rgba(255,255,255,0.1); }
        .person-name { font-weight: 600; flex: 1; }
        
        .person-actions { display: flex; gap: 8px; }
        .action-btn { 
            background: none; border: none; cursor: pointer; border-radius: 4px; 
            width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
            transition: 0.2s; color: rgba(255,255,255,0.6);
        }
        .edit-btn:hover { background: rgba(241, 196, 15, 0.2); color: #f1c40f; }
        .delete-btn:hover { background: rgba(231, 76, 60, 0.2); color: #e74c3c; }
        
        /* Edit Modal */
        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.7); backdrop-filter: blur(5px);
            display: flex; align-items: center; justify-content: center;
            opacity: 0; pointer-events: none; transition: 0.3s; z-index: 100;
        }
        .modal-overlay.active { opacity: 1; pointer-events: all; }
        .modal {
            background: #2c3e50; padding: 25px; border-radius: 12px; width: 350px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);
        }
        .modal h3 { margin-top: 0; }
        .modal input { 
            width: 100%; padding: 12px; margin-bottom: 20px; border-radius: 8px; 
            border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.2); 
            color: white; font-family: 'Poppins', sans-serif;
        }
        .modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
        .modal-btn { padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; }
        .btn-cancel { background: transparent; color: white; border: 1px solid rgba(255,255,255,0.2); }
        .btn-save { background: #2ecc71; color: white; }

        .restart-btn {
            margin-top: 15px; padding: 12px; border-radius: 8px; border: none; 
            background: linear-gradient(45deg, #e67e22, #d35400); color: white; 
            font-weight: bold; font-family: 'Poppins', sans-serif; cursor: pointer; 
            transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px;
            box-shadow: 0 4px 10px rgba(230, 126, 34, 0.4); text-transform: uppercase; letter-spacing: 1px;
        }
        .restart-btn:hover { background: linear-gradient(45deg, #d35400, #e67e22); box-shadow: 0 6px 15px rgba(230, 126, 34, 0.6); transform: translateY(-2px); }
        .restart-btn:active { transform: translateY(0); }

        /* Mobile Overlay Settings */
        .mobile-overlay {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); backdrop-filter: blur(5px); z-index: 40;
            opacity: 0; transition: 0.3s;
        }
        .mobile-overlay.active { opacity: 1; display: block; }
        
        .people-btn {
            display: none; position: fixed; top: 20px; right: 20px;
            background: rgba(0,0,0,0.5); backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2); color: white;
            padding: 10px 20px; border-radius: 50px; font-weight: bold; font-family: 'Poppins', sans-serif;
            cursor: pointer; z-index: 30; transition: 0.3s; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .people-btn:hover { background: rgba(0,0,0,0.8); }

        /* Media Queries for Mobile Responsiveness */
        @media (max-width: 800px) {
            body { flex-direction: column; justify-content: flex-start; }
            .main-content { padding-top: 80px; justify-content: flex-start; }
            
            .people-btn { display: flex; align-items: center; gap: 8px; }
            
            h1 { font-size: 2rem; }
            
            .wheel-container { width: 300px; height: 300px; }
            .pointer { border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 30px solid #ff4757; top: -10px; }
            .center-dot { width: 35px; height: 35px; }
            .label { font-size: 14px; }
            
            /* The labels need to be translated a bit less on smaller screens */
            .wheel-small .label { transform-origin: 0 0; }
            
            .spin-btn { padding: 12px 40px; font-size: 18px; margin-top: 20px; }
            #winner { font-size: 24px; margin-top: 15px; }
            
            /* Sidebar becomes a drawer/modal on mobile */
            .sidebar {
                position: fixed; right: -100%; top: 0; height: 100vh; width: 300px;
                z-index: 50; transition: right 0.3s ease;
                background: rgba(15, 32, 39, 0.95);
            }
            .sidebar.active { right: 0; }
            
            /* Close button inside sidebar */
            .close-sidebar-btn {
                display: block; background: none; border: none; color: white;
                font-size: 24px; cursor: pointer; float: right; margin-top: -5px; padding: 0;
            }
        }
        @media (min-width: 801px) {
            .close-sidebar-btn { display: none; }
        }

        /* Sabu3 Toggle */
        .sabu3-container {
            position: fixed; top: 20px; left: 20px; z-index: 30;
            display: flex; align-items: center; gap: 10px;
            background: rgba(0,0,0,0.5); backdrop-filter: blur(10px);
            padding: 10px 15px; border-radius: 50px; border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: 'Poppins', sans-serif;
            transition: 0.3s;
        }
        .sabu3-container:hover { background: rgba(0,0,0,0.8); }
        .sabu3-label { font-weight: bold; color: white; cursor: pointer; user-select: none; }
        
        .switch { position: relative; display: inline-block; width: 46px; height: 24px; margin: 0; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
            background-color: #ccc; transition: .4s; border-radius: 24px;
        }
        .slider:before {
            position: absolute; content: ""; height: 16px; width: 16px;
            left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%;
        }
        input:checked + .slider { background-color: #ff4757; box-shadow: 0 0 10px #ff4757; }
        input:focus + .slider { box-shadow: 0 0 1px #ff4757; }
        input:checked + .slider:before { transform: translateX(22px); }

        @keyframes pop { 0% { transform: scale(0.5); } 100% { transform: scale(1); } }
    </style>
</head>
<body>
    <div class="mobile-overlay" id="mobileOverlay" onclick="closeSidebar()"></div>
    
    <div class="sabu3-container">
        <label class="switch">
            <input type="checkbox" id="sabu3Mode">
            <span class="slider"></span>
        </label>
        <span class="sabu3-label" onclick="document.getElementById('sabu3Mode').click()">Sabu3 Mode <i class="fas fa-skull"></i></span>
    </div>

    <button class="people-btn" onclick="openSidebar()">
        <i class="fas fa-users"></i> People
    </button>

    <div class="main-content">
        <h1>innathe ira..</h1>
        
        <div class="wheel-container">
            <div class="pointer"></div>
            <div class="wheel" id="wheel">
                <div class="center-dot"></div>
                <div id="wheel-labels"></div>
            </div>
        </div>
        
        <button class="spin-btn" id="spinBtn" onclick="spin()">SPIN</button>
        <div id="winner"></div>
    </div>
    
    <div class="sidebar" id="sidebar">
        <h2>
            Manage Persons
            <button class="close-sidebar-btn" onclick="closeSidebar()"><i class="fas fa-times"></i></button>
        </h2>
        
        <div class="add-form">
            <input type="text" id="newPersonName" placeholder="Enter name...">
            <button onclick="addPerson()"><i class="fas fa-plus"></i></button>
        </div>
        
        <div class="person-list" id="personList">
            <!-- Rendered by JS -->
        </div>

        <button class="restart-btn" onclick="resetPersons()">
            <i class="fas fa-undo"></i> Restart (Reset List)
        </button>
    </div>

    <!-- Edit Modal -->
    <div class="modal-overlay" id="editModal">
        <div class="modal">
            <h3>Edit Person</h3>
            <input type="text" id="editPersonName">
            <input type="hidden" id="editPersonId">
            <div class="modal-actions">
                <button class="modal-btn btn-cancel" onclick="closeEditModal()">Cancel</button>
                <button class="modal-btn btn-save" onclick="saveEditPerson()">Save</button>
            </div>
        </div>
    </div>
    
    <!-- Sound Effect for winning -->
    <audio id="winSound" src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" preload="auto"></audio>

    <script>
        const COLORS = [
            "#FF5E5B", "#00CECB", "#FFED66", "#73D2DE", 
            "#218380", "#8F2D56", "#FAD02C", "#FF924C",
            "#9B5DE5", "#F15BB5", "#00BBF9"
        ];
        
        let persons = [];
        let numSegments = 0;
        let segmentAngle = 0;
        let currentRotation = 0;
        let isSpinning = false;
        
        // Setup Event Listeners
        document.getElementById('newPersonName').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') addPerson();
        });

        // Initialize App
        async function fetchPersons() {
            try {
                const response = await fetch('/api/persons');
                persons = await response.json();
                renderUI();
            } catch (error) {
                console.error("Error fetching persons:", error);
            }
        }

        function renderUI() {
            renderList();
            renderWheel();
            document.getElementById('spinBtn').disabled = persons.length < 2;
        }

        function renderList() {
            const listDiv = document.getElementById('personList');
            listDiv.innerHTML = '';
            
            if (persons.length === 0) {
                listDiv.innerHTML = '<div style="text-align:center; opacity:0.5; margin-top: 20px;">No persons added yet.</div>';
                return;
            }
            
            persons.forEach((person, index) => {
                const item = document.createElement('div');
                item.className = 'person-item';
                item.innerHTML = `
                    <span class="person-name">${person}</span>
                    <div class="person-actions">
                        <button class="action-btn edit-btn" onclick="openEditModal(${index}, '${person.replace(/'/g, "\\\\'")}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete-btn" onclick="deletePerson(${index})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;
                listDiv.appendChild(item);
            });
        }

        function renderWheel() {
            const wheel = document.getElementById('wheel');
            const labelsContainer = document.getElementById('wheel-labels');
            
            numSegments = persons.length;
            
            if (numSegments === 0) {
                wheel.style.background = '#2c3e50';
                labelsContainer.innerHTML = '';
                return;
            }
            
            const isMobile = window.innerWidth <= 800;
            const translateDist = isMobile ? 65 : 95; // Less translate on mobile
            
            if (numSegments === 1) {
                wheel.style.background = COLORS[0];
                labelsContainer.innerHTML = `<div class="label" style="transform: translate(-50%, -50%); color: #fff;">${persons[0]}</div>`;
                return;
            }

            segmentAngle = 360 / numSegments;
            let gradientParts = [];
            let labelsHtml = "";
            
            persons.forEach((person, i) => {
                const color = COLORS[i % COLORS.length];
                const startAngle = i * segmentAngle;
                const endAngle = (i + 1) * segmentAngle;
                gradientParts.push(`${color} ${startAngle}deg ${endAngle}deg`);
                
                const midAngle = startAngle + (segmentAngle / 2);
                const textRotation = midAngle - 90;
                
                const textColor = ['#FFED66', '#00CECB', '#73D2DE', '#FAD02C'].includes(color) ? '#333' : '#fff';
                
                labelsHtml += `
                <div class="label" style="transform: rotate(${textRotation}deg) translate(${translateDist}px, -50%); color: ${textColor}">
                    ${person}
                </div>`;
            });
            
            // Only set a conic gradient if there's more than 1 person, otherwise it gets weird.
            if (numSegments > 1) {
                wheel.style.background = `conic-gradient(${gradientParts.join(', ')})`;
            }
            labelsContainer.innerHTML = labelsHtml;
            
            // If wheel was already spinning, removing the transition causes issues.
            // Let the wheel transition continue if we are animating a deletion.
            if (!isSpinning) {
                // Re-apply rotation to prevent jump when updating
                wheel.style.transition = 'none';
                wheel.style.transform = `rotate(${currentRotation}deg)`;
                // Force reflow
                void wheel.offsetWidth;
                wheel.style.transition = 'transform 30s cubic-bezier(0.1, 0.9, 0.2, 1)';
            }
        }

        // --- API INTERACTIONS ---
        
        async function addPerson() {
            const input = document.getElementById('newPersonName');
            const name = input.value.trim();
            if (!name) return;
            
            try {
                const res = await fetch('/api/persons', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name })
                });
                if (res.ok) {
                    input.value = '';
                    fetchPersons();
                }
            } catch (e) { console.error(e); }
        }
        
        async function deletePerson(id) {
            try {
                const res = await fetch(`/api/persons/${id}`, { method: 'DELETE' });
                if (res.ok) fetchPersons();
            } catch (e) { console.error(e); }
        }
        
        async function resetPersons() {
            if(!confirm("Are you sure you want to reset the list to the original names?")) return;
            try {
                const res = await fetch('/api/persons/reset', { method: 'POST' });
                if (res.ok) fetchPersons();
            } catch (e) { console.error(e); }
        }
        
        function openEditModal(id, name) {
            document.getElementById('editPersonId').value = id;
            document.getElementById('editPersonName').value = name;
            document.getElementById('editModal').classList.add('active');
            document.getElementById('editPersonName').focus();
        }
        
        function closeEditModal() {
            document.getElementById('editModal').classList.remove('active');
        }
        
        async function saveEditPerson() {
            const id = document.getElementById('editPersonId').value;
            const name = document.getElementById('editPersonName').value.trim();
            if (!name) return;
            
            try {
                const res = await fetch(`/api/persons/${id}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name })
                });
                if (res.ok) {
                    closeEditModal();
                    fetchPersons();
                }
            } catch (e) { console.error(e); }
        }

        // --- SIDEBAR TOGGLE LOGIC ---
        function openSidebar() {
            document.getElementById('sidebar').classList.add('active');
            document.getElementById('mobileOverlay').classList.add('active');
        }
        
        function closeSidebar() {
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('mobileOverlay').classList.remove('active');
        }

        // --- SPIN LOGIC ---

        function spin() {
            if (isSpinning || persons.length < 2) return;
            isSpinning = true;
            
            const spinBtn = document.getElementById('spinBtn');
            const winnerDiv = document.getElementById('winner');
            const wheel = document.getElementById('wheel');
            const winSound = document.getElementById('winSound');
            
            // Disable all action buttons while spinning
            spinBtn.disabled = true;
            document.querySelectorAll('.action-btn, .add-form button').forEach(b => b.disabled = true);
            
            winnerDiv.classList.remove('show');
            winnerDiv.textContent = "";

            // Calculate random rotation: minimum 50 full spins + random stopping angle
            const extraSpins = Math.floor(Math.random() * 20 + 50); 
            const randomAngle = Math.floor(Math.random() * 360);
            
            currentRotation += (extraSpins * 360) + randomAngle;
            
            // Ensure transition is active before starting spin
            wheel.style.transition = 'transform 30s cubic-bezier(0.1, 0.9, 0.2, 1)';
            wheel.style.transform = `rotate(${currentRotation}deg)`;

            setTimeout(() => {
                const normalizedRotation = currentRotation % 360;
                const originalAngleAtTop = (360 - normalizedRotation) % 360;
                const winningIndex = Math.floor(originalAngleAtTop / segmentAngle);
                
                const selectedPerson = persons[winningIndex];
                const isSabu3 = document.getElementById('sabu3Mode').checked;
                
                if (isSabu3) {
                    if (persons.length > 2) {
                        winnerDiv.textContent = `❌ ${selectedPerson} is eliminated! ❌`;
                        winnerDiv.style.color = "#ff4757";
                        deletePerson(winningIndex, true);
                    } else if (persons.length === 2) {
                        const winnerIndex = winningIndex === 0 ? 1 : 0;
                        const grandWinner = persons[winnerIndex];
                        winnerDiv.textContent = `🏆 ${grandWinner} IS THE ULTIMATE WINNER! 🏆`;
                        winnerDiv.style.color = "#feca57";
                        deletePerson(winningIndex, true);
                    } else {
                        winnerDiv.textContent = `🏆 ${selectedPerson} is the only one left! 🏆`;
                        winnerDiv.style.color = "#feca57";
                    }
                } else {
                    winnerDiv.textContent = `🎉 It's ${selectedPerson}! 🎉`;
                    winnerDiv.style.color = "#feca57";
                }
                
                winnerDiv.classList.add('show');
                
                try { winSound.play(); } catch(e) {}
                
                setTimeout(() => {
                    isSpinning = false;
                    spinBtn.disabled = persons.length < 2;
                    document.querySelectorAll('.action-btn, .add-form button').forEach(b => b.disabled = false);
                }, 500); // Small delay to let deletion fetch complete and render
            }, 30000); 
        }

        // Handle window resize to re-render wheel labels correctly
        window.addEventListener('resize', () => {
            clearTimeout(window.resizeTimer);
            window.resizeTimer = setTimeout(renderWheel, 200);
        });

        // Run on load
        fetchPersons();
    </script>
</body>
</html>
"""

# HTML Routes
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

# API Routes
@app.route("/api/persons", methods=["GET"])
def get_persons():
    return jsonify(person_list)

@app.route("/api/persons", methods=["POST"])
def add_person():
    data = request.json
    name = data.get("name", "").strip()
    if name:
        person_list.append(name)
        return jsonify({"success": True, "person": name}), 201
    return jsonify({"error": "Name is required"}), 400

@app.route("/api/persons/<int:person_id>", methods=["PUT"])
def update_person(person_id):
    if 0 <= person_id < len(person_list):
        data = request.json
        name = data.get("name", "").strip()
        if name:
            person_list[person_id] = name
            return jsonify({"success": True, "person": name})
        return jsonify({"error": "Name is required"}), 400
    return jsonify({"error": "Person not found"}), 404

@app.route("/api/persons/<int:person_id>", methods=["DELETE"])
def delete_person(person_id):
    if 0 <= person_id < len(person_list):
        deleted = person_list.pop(person_id)
        return jsonify({"success": True, "deleted": deleted})
    return jsonify({"error": "Person not found"}), 404

@app.route("/api/persons/reset", methods=["POST"])
def reset_persons():
    global person_list
    person_list = list(DEFAULT_PERSONS)
    return jsonify({"success": True, "persons": person_list})

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
app = Flask(__name__)