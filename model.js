// 3D-модель квартиры по координатам из Homestyler V1.
// План: x — вправо, y — вниз от окон (метры). В three.js: x = x, z = y, высота — y.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const H = 2.7; // высота стен
const C = {
  wall: 0xe9e4dc, olive: 0x8e9078, tvwall: 0xb3aea6, tile: 0xb9bab8, oak: 0xc9a57a, darkwood: 0x7a5a43,
  white: 0xf3f2ef, graphite: 0x4a4d50, steel: 0x8a8d90, black: 0x26272a, greige: 0xdcd5c9, sage: 0xa9b39a,
  sofa: 0x7d8b6a, rug: 0x9a9893, cream: 0xe8e1d3, glass: 0xbfd6dc, green: 0x5e7d4f, art: 0x9aa3a0,
};

// стены: центр. линии, толщина 0.2; проёмы: [центр вдоль стены, ширина, низ, верх]
const WALLS = [
  [[-0.1, -0.1], [3.33, -0.1], [[1.43, 1.952, 0, 2.4]]],
  [[3.33, -0.1], [6.6, -0.1], [[4.78, 1.952, 0.5, 2.4]]],
  [[-0.1, -0.1], [-0.1, 4.55], []],
  [[-0.1, 4.55], [2.07, 4.55], []],
  [[2.07, 4.55], [3.33, 4.55], [[2.68, 0.9, 0, 2.1]]],
  [[3.33, -0.1], [3.33, 4.55], []],
  [[2.07, 4.55], [2.07, 9.4], []],
  [[2.07, 9.4], [3.94, 9.4], [[3.28, 0.96, 0, 2.1]]],
  [[3.94, 9.4], [6.6, 9.4], []],
  [[6.6, -0.1], [6.6, 9.4], []],
  [[3.94, 6.51], [6.6, 6.51], []],
  [[3.94, 6.51], [3.94, 9.4], [[7.36, 0.9, 0, 2.1]]],
];
const WINDOWS = [[1.43, 1.952, 0, 2.4], [4.78, 1.952, 0.5, 2.4]];

// мебель: x, y, поворот°, ширина, глубина, высота, низ, цвет
const BOXES = [
  // спальня
  [2.155, 2.35, 90, 1.7, 2.15, 0.5, 0, C.greige], [3.17, 2.35, 0, 0.1, 1.7, 1.05, 0, C.olive],
  [2.0, 2.35, 90, 1.72, 1.2, 0.04, 0.5, 0x6f6a63],
  [3.03, 3.45, 90, 0.45, 0.4, 0.47, 0, C.oak], [3.03, 1.25, 90, 0.45, 0.4, 0.47, 0, C.oak],
  [1.1, 4.15, 180, 2.2, 0.6, 2.6, 0, C.white], [2.01, 0.62, 127, 0.68, 0.8, 0.75, 0, C.sage],
  [1.258, 0.55, 0, 0.46, 0.46, 0.42, 0, C.oak], [3.03, 3.42, 90, 0.22, 0.2, 0.12, 0.47, C.black],
  [3.13, 0.55, 90, 0.8, 0.2, 0.28, 2.27, C.white],
  // гостиная
  [3.92, 3.16, 270, 2.25, 0.98, 0.42, 0, C.sofa], [3.53, 3.16, 0, 0.2, 2.25, 0.85, 0, C.sofa],
  [3.81, 1.05, 270, 1.6, 0.75, 0.04, 0.71, C.oak], [3.81, 0.3, 0, 0.75, 0.04, 0.71, 0, C.black],
  [3.81, 1.8, 0, 0.75, 0.04, 0.71, 0, C.black], [4.48, 1.05, 90, 0.6, 0.6, 1.1, 0, C.graphite],
  [3.52, 0.74, 270, 0.6, 0.05, 0.38, 0.8, C.black], [3.52, 1.36, 270, 0.6, 0.05, 0.38, 0.8, C.black],
  [3.61, 1.45, 270, 0.85, 0.35, 0.75, 1.9, C.white], [3.53, 0.55, 270, 0.8, 0.2, 0.28, 2.27, C.white],
  [6.47, 3.16, 90, 1.25, 0.05, 0.72, 1.0, C.black], [6.3, 3.16, 90, 1.6, 0.4, 0.3, 0.25, C.oak],
  [6.325, 3.16, 90, 1.6, 0.35, 0.55, 2.1, C.white], [5.076, 3.188, 90, 1.0, 0.55, 0.42, 0, C.darkwood],
  [5.041, 3.156, 90, 2.0, 1.6, 0.015, 0, C.rug], [6.3, 1.0, 90, 1.2, 0.4, 2.68, 0, C.white],
  [6.25, 2.1, 0, 0.3, 0.3, 0.8, 0, C.green], [3.445, 3.16, 270, 0.8, 0.03, 1.0, 1.05, C.art],
  [4.66, 1.84, 0, 0.04, 0.04, 1.3, 0, C.black], [4.66, 1.84, 0, 0.36, 0.36, 0.3, 1.28, C.cream],
  // кухня
  [6.19, 4.91, 90, 0.6, 0.62, 1.95, 0, C.steel], [6.2, 4.91, 90, 0.6, 0.6, 0.7, 1.97, C.graphite],
  [4.15, 6.11, 180, 0.6, 0.6, 2.6, 0, C.graphite],
  [4.15, 5.8, 0, 0.56, 0.02, 0.58, 0.56, C.black], [4.15, 5.8, 0, 0.56, 0.02, 0.4, 1.17, C.black],
  [5.475, 6.11, 0, 2.05, 0.6, 0.88, 0, C.graphite], [6.2, 5.51, 0, 0.6, 0.6, 0.88, 0, C.graphite],
  [5.475, 6.1, 0, 2.05, 0.62, 0.04, 0.88, 0x9c9a96], [6.19, 5.51, 0, 0.62, 0.6, 0.04, 0.88, 0x9c9a96],
  [5.4, 6.12, 0, 0.59, 0.52, 0.01, 0.92, C.black], [6.21, 5.51, 90, 0.5, 0.45, 0.01, 0.92, C.black],
  [6.325, 5.51, 90, 0.6, 0.35, 1.1, 1.55, C.graphite], [6.325, 6.11, 90, 0.6, 0.35, 1.1, 1.55, C.graphite],
  [5.175, 6.23, 180, 1.45, 0.35, 1.1, 1.55, C.graphite],
  // прихожая
  [2.47, 6.35, 270, 1.3, 0.6, 2.68, 0, C.white], [2.47, 7.3, 270, 0.6, 0.6, 2.68, 0, C.white],
  [2.47, 7.85, 270, 0.5, 0.6, 2.68, 0, C.white], [2.34, 8.537, 270, 0.8, 0.35, 0.85, 0, C.graphite],
  [3.825, 8.5, 90, 0.6, 0.03, 1.8, 0.3, C.glass],
  // санузел
  [4.9, 7.06, 0, 0.02, 0.9, 2.0, 0, C.glass, true], [6.27, 8.1, 90, 0.8, 0.46, 0.45, 0.4, C.oak],
  [6.3, 8.1, 90, 0.6, 0.4, 0.08, 0.85, C.white], [6.43, 8.1, 90, 0.7, 0.12, 0.7, 1.15, C.glass],
  [6.19, 8.92, 90, 0.37, 0.55, 0.4, 0.0, C.white], [6.325, 8.905, 90, 0.75, 0.35, 1.2, 1.5, C.oak],
  [4.55, 6.785, 0, 0.6, 0.35, 2.0, 0, C.oak], [5.039, 9.0, 180, 0.6, 0.6, 1.76, 0, C.black],
  [4.08, 8.1, 270, 0.52, 0.06, 0.95, 0.6, C.black], [4.275, 8.6, 270, 0.45, 0.47, 0.58, 0, 0x3a3c3e],
  [4.315, 9.075, 0, 0.55, 0.45, H, 0, C.wall],
  // треки
  [4.95, 2.2, 90, 2.0, 0.03, 0.03, 2.66, C.black], [5.25, 5.15, 0, 1.5, 0.03, 0.03, 2.66, C.black],
];
// рейки-перегородка: 15 брусков 40×40 с шагом 40
for (let i = 0; i < 15; i++) BOXES.push([5.32 + i * 0.08, 4.33, 0, 0.04, 0.07, H, 0, C.oak]);
// шторы — по краям окон
for (const x of [0.32, 2.54, 3.68, 5.88]) BOXES.push([x, 0.1, 0, 0.32, 0.06, 2.6, 0.02, C.sage]);

// покраска стен (тонкие плоскости поверх)
const PAINT = [
  [3.225, 2.225, 90, 4.45, C.olive], [6.497, 2.15, 90, 4.3, C.tvwall], [0.003, 2.2, 90, 4.4, 0xf6f4f0],
  [5.27, 6.613, 0, 2.46, C.tile], [5.27, 9.297, 0, 2.46, C.tile], [4.043, 7.955, 90, 2.69, C.tile], [6.497, 7.955, 90, 2.69, C.tile],
];
const FLOORS = [ // x0, y0, x1, y1, цвет
  [0, 0, 3.23, 4.45, C.oak], [3.23, 0, 6.5, 6.41, C.oak], [2.17, 4.45, 3.23, 9.3, C.oak],
  [3.23, 6.41, 3.84, 9.3, C.oak], [3.84, 6.41, 4.04, 6.61, C.oak], [4.04, 6.61, 6.5, 9.3, C.tile],
];

export function mount(el) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xeeeae4);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  el.appendChild(renderer.domElement);

  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
  camera.position.set(3.25, 11.5, 4.65 + 8);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(3.25, 0.6, 4.65);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI / 2.05;
  controls.minDistance = 3; controls.maxDistance = 25;

  scene.add(new THREE.HemisphereLight(0xffffff, 0xb8a990, 1.6));
  const sun = new THREE.DirectionalLight(0xfff4e5, 1.6);
  sun.position.set(-3, 9, -6); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8 });
  sun.target.position.set(3.25, 0, 4.65);
  scene.add(sun, sun.target);

  const mats = new Map();
  const mat = (color, glass) => {
    const k = color + (glass ? 'g' : '');
    if (!mats.has(k)) mats.set(k, new THREE.MeshStandardMaterial({ color, roughness: 0.85,
      transparent: !!glass, opacity: glass ? 0.35 : 1 }));
    return mats.get(k);
  };
  const box = (w, h, d, color, glass) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(color, glass));
    m.castShadow = !glass; m.receiveShadow = true;
    return m;
  };

  const walls = new THREE.Group();
  for (const [a, b, ops] of WALLS) {
    const horiz = a[1] === b[1];
    const s0 = horiz ? a[0] : a[1], s1 = horiz ? b[0] : b[1], c = horiz ? a[1] : a[0];
    const piece = (p0, p1, y0, y1) => {
      if (p1 - p0 < 0.001 || y1 - y0 < 0.001) return;
      const len = p1 - p0 + (p0 === s0 ? 0.1 : 0) + (p1 === s1 ? 0.1 : 0);
      const mid = (p0 - (p0 === s0 ? 0.1 : 0) + p1 + (p1 === s1 ? 0.1 : 0)) / 2;
      const m = horiz ? box(len, y1 - y0, 0.2, C.wall) : box(0.2, y1 - y0, len, C.wall);
      m.position.set(horiz ? mid : c, (y0 + y1) / 2, horiz ? c : mid);
      walls.add(m);
    };
    let cur = s0;
    for (const [oc, ow, lo, hi] of [...ops].sort((p, q) => p[0] - q[0])) {
      piece(cur, oc - ow / 2, 0, H);
      piece(oc - ow / 2, oc + ow / 2, 0, lo);
      piece(oc - ow / 2, oc + ow / 2, hi, H);
      cur = oc + ow / 2;
    }
    piece(cur, s1, 0, H);
  }
  for (const [x, z, r, len, color] of PAINT) {
    const p = new THREE.Mesh(new THREE.PlaneGeometry(len, H), mat(color));
    p.position.set(x, H / 2, z); p.rotation.y = r * Math.PI / 180; p.receiveShadow = true;
    p.material.side = THREE.DoubleSide;
    walls.add(p);
  }
  for (const [c, w, lo, hi] of WINDOWS) {
    const g = box(w, hi - lo, 0.02, C.glass, true);
    g.position.set(c, (lo + hi) / 2, -0.1);
    walls.add(g);
  }
  scene.add(walls);

  for (const [x0, y0, x1, y1, color] of FLOORS) {
    const f = box(x1 - x0, 0.02, y1 - y0, color);
    f.position.set((x0 + x1) / 2, -0.01, (y0 + y1) / 2); f.castShadow = false;
    scene.add(f);
  }
  const furniture = new THREE.Group();
  furniture.visible = false;
  const rug = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.015, 48), mat(C.cream));
  rug.position.set(1.1, 0.008, 0.75); rug.receiveShadow = true;
  furniture.add(rug);
  for (const [x, y, r, w, d, h, z, color, glass] of BOXES) {
    const m = box(w, h, d, color, glass);
    m.position.set(x, z + h / 2, y);
    m.rotation.y = r * Math.PI / 180;
    furniture.add(m);
  }
  scene.add(furniture);

  const resize = () => {
    const w = el.clientWidth, h = el.clientHeight;
    renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(el);
  resize();
  renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });

  return {
    // срез на 1,1 м — как кукольный домик, видно всё внутри
    setLowWalls(low) { renderer.clippingPlanes = low ? [new THREE.Plane(new THREE.Vector3(0, -1, 0), 1.1)] : []; },
    setFurniture(on) { furniture.visible = on; },
  };
}
