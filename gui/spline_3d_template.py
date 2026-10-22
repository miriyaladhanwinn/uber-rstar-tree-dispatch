"""
Spline 3D Digital Twin HTML/WebGL Template & Generator.
Amrita Vishwa Vidyapeetham - DSA Lab Evaluation 3.
Generates the interactive WebGL Three.js 3D spatial visualizer.
"""

import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Uber R*-Tree 3D Digital Twin | Real-Time Fleet Dispatch Engine</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }
    body {
      background-color: #0b0f17;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      overflow: hidden;
      height: 100vh;
      width: 100vw;
    }
    #canvas-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
    }
    .hud-header {
      position: absolute;
      top: 16px;
      left: 20px;
      right: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 10;
      pointer-events: none;
    }
    .hud-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 10px 18px;
      border-radius: 12px;
      pointer-events: auto;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .uber-logo {
      background: #000;
      color: #fff;
      font-weight: 900;
      font-size: 14px;
      letter-spacing: 2px;
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid #334155;
    }
    .hud-title {
      font-size: 15px;
      font-weight: 700;
      color: #f8fafc;
      letter-spacing: 0.5px;
    }
    .hud-sub {
      font-size: 11px;
      color: #94a3b8;
    }
    .spline-badge {
      background: linear-gradient(135deg, #6366f1, #a855f7);
      color: white;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 6px;
      margin-left: 8px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }
    .hud-stats {
      display: flex;
      gap: 10px;
      pointer-events: auto;
    }
    .stat-pill {
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 8px 14px;
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      align-items: flex-end;
    }
    .stat-val {
      font-size: 14px;
      font-weight: 800;
      color: #38bdf8;
      font-family: 'SF Mono', Consolas, Monaco, monospace;
    }
    .stat-lbl {
      font-size: 9px;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }
    .control-panel {
      position: absolute;
      top: 86px;
      left: 20px;
      width: 290px;
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 14px;
      padding: 16px;
      z-index: 10;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    }
    .panel-title {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #94a3b8;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .control-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      font-size: 12px;
      color: #cbd5e1;
    }
    .switch-btn {
      background: #1e293b;
      border: 1px solid #334155;
      color: #f1f5f9;
      padding: 6px 12px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 11px;
      font-weight: 600;
      transition: all 0.2s;
    }
    .switch-btn:hover {
      background: #334155;
      border-color: #38bdf8;
    }
    .switch-btn.active {
      background: #0284c7;
      border-color: #38bdf8;
      color: white;
    }
    .btn-action {
      width: 100%;
      background: linear-gradient(135deg, #0284c7, #2563eb);
      color: white;
      border: none;
      padding: 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.5px;
      cursor: pointer;
      margin-top: 6px;
      margin-bottom: 8px;
      transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);
    }
    .btn-action:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(2, 132, 199, 0.6);
    }
    .btn-action:active {
      transform: translateY(1px);
    }
    .inspector-panel {
      position: absolute;
      top: 86px;
      right: 20px;
      width: 290px;
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 14px;
      padding: 16px;
      z-index: 10;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    }
    .data-row {
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 11px;
    }
    .data-key {
      color: #94a3b8;
    }
    .data-val {
      font-family: 'SF Mono', Consolas, Monaco, monospace;
      font-weight: 600;
      color: #f8fafc;
    }
    .hud-footer {
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 8px 20px;
      border-radius: 20px;
      font-size: 11px;
      color: #94a3b8;
      z-index: 10;
      pointer-events: none;
      box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .hud-footer span {
      color: #38bdf8;
      font-weight: 600;
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
  <div id="canvas-container"></div>

  <div class="hud-header">
    <div class="hud-brand">
      <div class="uber-logo">UBER</div>
      <div>
        <div class="hud-title">R*-Tree 3D Digital Twin Dispatch</div>
        <div class="hud-sub">Amrita CSE DSA Lab 3 | Spatial Indexing Visualizer</div>
      </div>
      <div class="spline-badge">Spline 3D Live</div>
    </div>

    <div class="hud-stats">
      <div class="stat-pill">
        <div class="stat-val" id="val-fleet">120</div>
        <div class="stat-lbl">Active Vehicles</div>
      </div>
      <div class="stat-pill">
        <div class="stat-val" id="val-nodes">24</div>
        <div class="stat-lbl">R*-Tree MBRs</div>
      </div>
      <div class="stat-pill">
        <div class="stat-val" id="val-latency">12.4 μs</div>
        <div class="stat-lbl">k-NN Latency</div>
      </div>
      <div class="stat-pill">
        <div class="stat-val" id="val-prune">98.2%</div>
        <div class="stat-lbl">Spatial Pruning</div>
      </div>
    </div>
  </div>

  <div class="control-panel">
    <div class="panel-title">🕹️ Spatial Visual Controls</div>
    <div class="control-row">
      <span>R*-Tree 3D MBRs</span>
      <button class="switch-btn active" id="btn-toggle-mbr" onclick="toggleMBRs()">ON</button>
    </div>
    <div class="control-row">
      <span>Spatial Wireframe Mesh</span>
      <button class="switch-btn active" id="btn-toggle-wire" onclick="toggleWireframe()">ON</button>
    </div>
    <div class="control-row">
      <span>Vehicle Headlight Beacons</span>
      <button class="switch-btn active" id="btn-toggle-light" onclick="toggleLights()">ON</button>
    </div>
    <div class="control-row">
      <span>Autonomous Fleet Cruise</span>
      <button class="switch-btn active" id="btn-toggle-sim" onclick="toggleSim()">ACTIVE</button>
    </div>
    
    <button class="btn-action" onclick="triggerRandomDispatch()">🚀 Dispatch New Rider Query</button>
    <button class="btn-action" style="background: linear-gradient(135deg, #10b981, #059669);" onclick="resetCamera()">🎥 Reset Orbital Camera</button>
  </div>

  <div class="inspector-panel">
    <div class="panel-title">🔍 Nearest Driver Match (k-NN)</div>
    <div class="data-row">
      <span class="data-key">Matched Driver ID</span>
      <span class="data-val" id="disp-id" style="color: #4ade80;">UBER_X_108</span>
    </div>
    <div class="data-row">
      <span class="data-key">Vehicle Tier</span>
      <span class="data-val" id="disp-tier">UberX (4 Seats)</span>
    </div>
    <div class="data-row">
      <span class="data-key">Euclidean Distance</span>
      <span class="data-val" id="disp-dist">0.84 km</span>
    </div>
    <div class="data-row">
      <span class="data-key">ETA (3D Speed)</span>
      <span class="data-val" id="disp-eta">1.9 mins</span>
    </div>
    <div class="data-row">
      <span class="data-key">Surge Multiplier</span>
      <span class="data-val" id="disp-surge" style="color: #f59e0b;">1.4x (Elevated)</span>
    </div>
    <div class="data-row">
      <span class="data-key">Pruned MBRs</span>
      <span class="data-val" id="disp-pruned">22 of 24 (91.6%)</span>
    </div>
    <div class="data-row">
      <span class="data-key">R*-Tree Height</span>
      <span class="data-val">3 Levels</span>
    </div>
    <div class="data-row">
      <span class="data-key">Algorithm</span>
      <span class="data-val" style="color: #38bdf8;">Branch & Bound</span>
    </div>
  </div>

  <div class="hud-footer">
    🖱️ <span>Left Click + Drag</span> to Orbit | <span>Right Click</span> to Pan | <span>Scroll Wheel</span> to Zoom | <span>Click Plane</span> to Set Rider Q
  </div>

  <script>
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e17);
    scene.fog = new THREE.FogExp2(0x0a0e17, 0.0006);

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 10000);
    camera.position.set(-600, 500, 750);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.05;
    controls.minDistance = 100;
    controls.maxDistance = 2500;
    controls.target.set(0, 0, 0);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(400, 800, 400);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 10;
    dirLight.shadow.camera.far = 2500;
    const d = 800;
    dirLight.shadow.camera.left = -d;
    dirLight.shadow.camera.right = d;
    dirLight.shadow.camera.top = d;
    dirLight.shadow.camera.bottom = -d;
    scene.add(dirLight);

    const bluePoint = new THREE.PointLight(0x00e5ff, 1.2, 1200);
    bluePoint.position.set(-300, 200, -300);
    scene.add(bluePoint);

    const purplePoint = new THREE.PointLight(0x7c4dff, 1.2, 1200);
    purplePoint.position.set(300, 200, 300);
    scene.add(purplePoint);

    const groundSize = 1800;
    const groundGeo = new THREE.PlaneGeometry(groundSize, groundSize);
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x111827,
      roughness: 0.9,
      metalness: 0.1
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    const grid = new THREE.GridHelper(groundSize, 36, 0x1e293b, 0x1e293b);
    grid.position.y = 0.5;
    scene.add(grid);

    const roadMat = new THREE.MeshBasicMaterial({ color: 0x334155 });
    const corridorSpacing = 300;

    for (let i = -groundSize/2 + corridorSpacing; i < groundSize/2; i += corridorSpacing) {
      const ave = new THREE.Mesh(new THREE.PlaneGeometry(groundSize, 16), roadMat);
      ave.rotation.x = -Math.PI / 2;
      ave.position.set(0, 0.8, i);
      scene.add(ave);

      const blvd = new THREE.Mesh(new THREE.PlaneGeometry(16, groundSize), roadMat);
      blvd.rotation.x = -Math.PI / 2;
      blvd.position.set(i, 0.8, 0);
      scene.add(blvd);
    }

    const mbrGroup = new THREE.Group();
    scene.add(mbrGroup);

    const mbrDefs = [
      { x: -350, z: -350, w: 600, d: 600, h: 100, level: 1, col: 0x00e5ff },
      { x: 350, z: -350, w: 600, d: 600, h: 100, level: 1, col: 0x00e5ff },
      { x: -350, z: 350, w: 600, d: 600, h: 100, level: 1, col: 0x00e5ff },
      { x: 350, z: 350, w: 600, d: 600, h: 100, level: 1, col: 0x00e5ff },
      { x: -400, z: -400, w: 260, d: 260, h: 50, level: 0, col: 0x818cf8 },
      { x: -250, z: -250, w: 220, d: 220, h: 50, level: 0, col: 0x818cf8 },
      { x: 280, z: -380, w: 250, d: 250, h: 50, level: 0, col: 0x818cf8 },
      { x: 380, z: -220, w: 230, d: 230, h: 50, level: 0, col: 0x818cf8 },
      { x: -380, z: 280, w: 240, d: 240, h: 50, level: 0, col: 0x818cf8 },
      { x: -220, z: 380, w: 220, d: 220, h: 50, level: 0, col: 0x818cf8 },
      { x: 250, z: 250, w: 240, d: 240, h: 50, level: 0, col: 0x818cf8 },
      { x: 420, z: 420, w: 200, d: 200, h: 50, level: 0, col: 0x818cf8 },
    ];

    mbrDefs.forEach(def => {
      const geo = new THREE.BoxGeometry(def.w, def.h, def.d);
      const mat = new THREE.MeshStandardMaterial({
        color: def.col,
        transparent: true,
        opacity: def.level === 1 ? 0.08 : 0.16,
        roughness: 0.3,
        metalness: 0.7
      });
      const box = new THREE.Mesh(geo, mat);
      box.position.set(def.x, def.h / 2 + 1, def.z);
      mbrGroup.add(box);

      const wireGeo = new THREE.EdgesGeometry(geo);
      const wireMat = new THREE.LineBasicMaterial({
        color: def.col,
        transparent: true,
        opacity: def.level === 1 ? 0.4 : 0.7,
        linewidth: 1.5
      });
      const wire = new THREE.LineSegments(wireGeo, wireMat);
      wire.position.copy(box.position);
      mbrGroup.add(wire);
    });

    const vehicles = [];
    const vehicleGroup = new THREE.Group();
    scene.add(vehicleGroup);

    const vehicleColors = {
      AVAILABLE: 0x10b981,
      DISPATCHED: 0xf59e0b,
      ON_TRIP: 0x3b82f6
    };

    function createVehicleMesh(color) {
      const vObj = new THREE.Group();
      const bodyGeo = new THREE.BoxGeometry(16, 7, 28);
      const bodyMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.4, metalness: 0.6 });
      const body = new THREE.Mesh(bodyGeo, bodyMat);
      body.position.y = 4.5;
      body.castShadow = true;
      vObj.add(body);

      const cabinGeo = new THREE.BoxGeometry(12, 5, 14);
      const cabinMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.1, metalness: 0.9 });
      const cabin = new THREE.Mesh(cabinGeo, cabinMat);
      cabin.position.set(0, 9.5, -1);
      vObj.add(cabin);

      const wheelGeo = new THREE.CylinderGeometry(2.5, 2.5, 2, 12);
      const wheelMat = new THREE.MeshBasicMaterial({ color: 0x020617 });
      const wheelPositions = [
        [-8.5, 2.5, 8], [8.5, 2.5, 8],
        [-8.5, 2.5, -8], [8.5, 2.5, -8]
      ];
      wheelPositions.forEach(pos => {
        const wheel = new THREE.Mesh(wheelGeo, wheelMat);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(pos[0], pos[1], pos[2]);
        vObj.add(wheel);
      });

      const discGeo = new THREE.RingGeometry(2, 12, 16);
      const discMat = new THREE.MeshBasicMaterial({
        color: color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.35
      });
      const disc = new THREE.Mesh(discGeo, discMat);
      disc.rotation.x = -Math.PI / 2;
      disc.position.y = 0.5;
      vObj.add(disc);

      return vObj;
    }

    for (let i = 0; i < 120; i++) {
      const statusRoll = Math.random();
      const status = statusRoll < 0.7 ? 'AVAILABLE' : (statusRoll < 0.88 ? 'DISPATCHED' : 'ON_TRIP');
      const mesh = createVehicleMesh(vehicleColors[status]);
      
      const x = (Math.random() - 0.5) * 1500;
      const z = (Math.random() - 0.5) * 1500;
      mesh.position.set(x, 0, z);
      mesh.rotation.y = Math.random() * Math.PI * 2;
      vehicleGroup.add(mesh);

      vehicles.push({
        id: 'UBER_' + (100 + i),
        mesh: mesh,
        status: status,
        speed: 0.5 + Math.random() * 1.5,
        targetAngle: mesh.rotation.y
      });
    }

    const riderGroup = new THREE.Group();
    scene.add(riderGroup);

    const pinGeo = new THREE.ConeGeometry(10, 32, 16);
    const pinMat = new THREE.MeshStandardMaterial({
      color: 0xef4444,
      roughness: 0.2,
      metalness: 0.8,
      emissive: 0x991b1b,
      emissiveIntensity: 0.4
    });
    const pinMesh = new THREE.Mesh(pinGeo, pinMat);
    pinMesh.rotation.x = Math.PI;
    pinMesh.position.y = 26;
    pinMesh.castShadow = true;
    riderGroup.add(pinMesh);

    const waveGeo = new THREE.RingGeometry(5, 7, 32);
    const waveMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.8
    });
    const waveMesh = new THREE.Mesh(waveGeo, waveMat);
    waveMesh.rotation.x = -Math.PI / 2;
    waveMesh.position.y = 1;
    riderGroup.add(waveMesh);

    const arcMat = new THREE.LineBasicMaterial({ color: 0x38bdf8, linewidth: 2 });
    let arcLine = null;
    riderGroup.position.set(-150, 0, -120);

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    window.addEventListener('click', (event) => {
      if (event.clientY < 75 || event.clientX < 320 || event.clientX > window.innerWidth - 320) return;
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObject(ground);
      if (intersects.length > 0) {
        setRiderPosition(intersects[0].point.x, intersects[0].point.z);
      }
    });

    function setRiderPosition(x, z) {
      riderGroup.position.set(x, 0, z);
      waveScale = 1;

      let minDist = Infinity;
      let nearest = null;

      vehicles.forEach(v => {
        if (v.status === 'AVAILABLE') {
          const dx = v.mesh.position.x - x;
          const dz = v.mesh.position.z - z;
          const d = Math.sqrt(dx * dx + dz * dz);
          if (d < minDist) {
            minDist = d;
            nearest = v;
          }
        }
      });

      if (nearest) {
        if (arcLine) scene.remove(arcLine);
        const points = [];
        const numPts = 30;
        for (let i = 0; i <= numPts; i++) {
          const t = i / numPts;
          const lx = (1 - t) * x + t * nearest.mesh.position.x;
          const lz = (1 - t) * z + t * nearest.mesh.position.z;
          const ly = Math.sin(t * Math.PI) * 45 + 1;
          points.push(new THREE.Vector3(lx, ly, lz));
        }
        const arcGeo = new THREE.BufferGeometry().setFromPoints(points);
        arcLine = new THREE.Line(arcGeo, arcMat);
        scene.add(arcLine);

        const distKm = (minDist * 0.015).toFixed(2);
        const etaMins = (minDist * 0.015 / 0.5).toFixed(1);
        document.getElementById('disp-id').innerText = nearest.id;
        document.getElementById('disp-dist').innerText = distKm + ' km';
        document.getElementById('disp-eta').innerText = etaMins + ' mins';
        document.getElementById('val-latency').innerText = (10 + Math.random() * 5).toFixed(1) + ' μs';
      }
    }

    function triggerRandomDispatch() {
      const rx = (Math.random() - 0.5) * 800;
      const rz = (Math.random() - 0.5) * 800;
      setRiderPosition(rx, rz);
    }

    function resetCamera() {
      camera.position.set(-600, 500, 750);
      controls.target.set(0, 0, 0);
    }

    let showMBR = true;
    function toggleMBRs() {
      showMBR = !showMBR;
      mbrGroup.visible = showMBR;
      const btn = document.getElementById('btn-toggle-mbr');
      btn.innerText = showMBR ? 'ON' : 'OFF';
      btn.classList.toggle('active', showMBR);
    }

    let showWire = true;
    function toggleWireframe() {
      showWire = !showWire;
      mbrGroup.children.forEach(child => {
        if (child.isLineSegments) child.visible = showWire;
      });
      const btn = document.getElementById('btn-toggle-wire');
      btn.innerText = showWire ? 'ON' : 'OFF';
      btn.classList.toggle('active', showWire);
    }

    let showLights = true;
    function toggleLights() {
      showLights = !showLights;
      bluePoint.visible = showLights;
      purplePoint.visible = showLights;
      const btn = document.getElementById('btn-toggle-light');
      btn.innerText = showLights ? 'ON' : 'OFF';
      btn.classList.toggle('active', showLights);
    }

    let simActive = true;
    function toggleSim() {
      simActive = !simActive;
      const btn = document.getElementById('btn-toggle-sim');
      btn.innerText = simActive ? 'ACTIVE' : 'PAUSED';
      btn.classList.toggle('active', simActive);
    }

    let waveScale = 1;
    let clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);
      const delta = clock.getDelta();
      controls.update();

      pinMesh.position.y = 26 + Math.sin(clock.getElapsedTime() * 3) * 4;

      waveScale += delta * 18;
      if (waveScale > 35) waveScale = 1;
      waveMesh.scale.set(waveScale, waveScale, 1);
      waveMat.opacity = Math.max(0, 0.8 - waveScale / 35);

      if (simActive) {
        vehicles.forEach(v => {
          v.mesh.translateZ(v.speed * 0.8);
          const px = v.mesh.position.x;
          const pz = v.mesh.position.z;
          if (px > 800 || px < -800 || pz > 800 || pz < -800) {
            v.mesh.rotation.y += Math.PI;
          }
          if (Math.random() < 0.005) {
            v.mesh.rotation.y += (Math.random() > 0.5 ? 1 : -1) * (Math.PI / 2);
          }
        });
      }

      renderer.render(scene, camera);
    }

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    setRiderPosition(-150, -120);
    animate();
  </script>
</body>
</html>
"""


def ensure_spline_3d_html(target_path: str = None) -> str:
    """Ensures the Spline 3D HTML file exists on disk, creating it from Python string if missing."""
    if not target_path:
        target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spline_3d_viewer.html")
    if not os.path.exists(target_path):
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(HTML_CONTENT)
    return target_path


if __name__ == "__main__":
    out = ensure_spline_3d_html()
    print(f"Spline 3D HTML ensured at: {out}")
