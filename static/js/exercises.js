/* ============================================================
   GYM EXERCISE VIEWER — exercises.js
   All 26 exercises with canvas animations
   ============================================================ */

/* ── Exercise Data ─────────────────────────────────────────── */
const DATA = {
  "Chest & Triceps": {
    color: "#D85A30",
    icon: "💪",
    exercises: {
      "Bench Press":          { muscles: ["chest","triceps","front delt"],       tips: "Keep shoulder blades retracted, feet flat on the floor.", phases: ["lower","press"],         anim: "benchPress" },
      "Incline Dumbbell Press":{ muscles: ["upper chest","triceps"],              tips: "Set bench at 30–45°. Controls the negative slowly.",      phases: ["lower","press"],         anim: "inclinePress" },
      "Cable Flyes":          { muscles: ["chest","front delt"],                 tips: "Maintain a slight elbow bend throughout the arc.",          phases: ["open","close"],          anim: "cableFlye" },
      "Triceps Pushdown":     { muscles: ["triceps"],                            tips: "Pin elbows to sides. Fully extend at the bottom.",          phases: ["push","return"],         anim: "pushdown" },
      "Skull Crushers":       { muscles: ["triceps long head"],                  tips: "Lower bar toward forehead, keep upper arms vertical.",      phases: ["lower","extend"],        anim: "skullCrusher" },
      "Push-ups":             { muscles: ["chest","triceps","shoulders"],        tips: "Body straight as a plank. Core tight throughout.",          phases: ["lower","push"],          anim: "pushup" }
    }
  },
  "Back & Biceps": {
    color: "#185FA5",
    icon: "🏋️",
    exercises: {
      "Pull-ups":       { muscles: ["lats","biceps","rhomboids"],   tips: "Dead hang at bottom, chin fully over bar at top.",       phases: ["hang","pull","lower"],    anim: "pullup" },
      "Barbell Row":    { muscles: ["lats","rhomboids","biceps"],   tips: "Hinge at hips, pull bar to lower chest or navel.",       phases: ["lower","row"],            anim: "barbellRow" },
      "Lat Pulldown":   { muscles: ["lats","teres major"],          tips: "Pull to upper chest, slight lean back, squeeze lats.",   phases: ["up","pull"],              anim: "latPulldown" },
      "Bicep Curls":    { muscles: ["biceps","brachialis"],         tips: "No swinging — strict form. Squeeze at the top.",         phases: ["lower","curl"],           anim: "bicepCurl" },
      "Hammer Curls":   { muscles: ["brachialis","brachioradialis"],tips: "Neutral grip throughout. Control the descent.",          phases: ["lower","curl"],           anim: "hammerCurl" }
    }
  },
  "Legs": {
    color: "#3B6D11",
    icon: "🦵",
    exercises: {
      "Barbell Squat":       { muscles: ["quads","glutes","hamstrings"], tips: "Knees track toes, chest tall, break parallel.",         phases: ["descend","ascend"],       anim: "squat" },
      "Leg Press":           { muscles: ["quads","glutes"],              tips: "Don't lock knees at top. Full range of motion.",         phases: ["push","return"],          anim: "legPress" },
      "Romanian Deadlift":   { muscles: ["hamstrings","glutes"],         tips: "Hinge at hips. Bar stays close to legs throughout.",     phases: ["hinge","extend"],         anim: "rdl" },
      "Leg Curls":           { muscles: ["hamstrings"],                  tips: "Full range of motion. Pause at the top contraction.",    phases: ["extend","curl"],          anim: "legCurl" },
      "Calf Raises":         { muscles: ["gastrocnemius","soleus"],      tips: "Full stretch at the bottom. Rise to full extension.",    phases: ["lower","raise"],          anim: "calfRaise" }
    }
  },
  "Shoulders": {
    color: "#854F0B",
    icon: "🔝",
    exercises: {
      "Overhead Press": { muscles: ["front delt","mid delt","triceps"], tips: "Press in a straight line. Brace core throughout.",       phases: ["lower","press"],          anim: "ohp" },
      "Lateral Raise":  { muscles: ["mid delt"],                       tips: "Lead with elbows, slight forward lean. Don't swing.",     phases: ["lower","raise"],          anim: "lateralRaise" },
      "Front Raise":    { muscles: ["front delt"],                     tips: "Raise to shoulder height. Control the descent.",          phases: ["lower","raise"],          anim: "frontRaise" },
      "Face Pulls":     { muscles: ["rear delt","rotator cuff"],       tips: "Pull to nose level, externally rotate at the end.",       phases: ["extend","pull"],          anim: "facePull" },
      "Shrugs":         { muscles: ["trapezius"],                      tips: "Straight up — no rolling. Hold the peak contraction.",    phases: ["lower","shrug"],          anim: "shrug" }
    }
  },
  "Full Body / Core": {
    color: "#993556",
    icon: "⚡",
    exercises: {
      "Deadlift":      { muscles: ["hamstrings","glutes","lats","traps","spinal erectors"], tips: "Bar over mid-foot. Neutral spine. Drive through the floor.", phases: ["set","pull","lower"], anim: "deadlift" },
      "Plank":         { muscles: ["core","shoulders","glutes"],                           tips: "Squeeze everything. No hip sag or raised hips.",             phases: ["hold"],              anim: "plank" },
      "Treadmill Run": { muscles: ["quads","calves","glutes","core"],                      tips: "Land midfoot. Relax shoulders. Arms at 90°.",                phases: ["stride","push","flight"], anim: "run" }
    }
  }
};

/* ── Drawing Helpers ───────────────────────────────────────── */

const BODY_COLOR  = "#7F77DD";
const ARM_COLOR   = "#1D9E75";
const SKIN_COLOR  = "#EF9F27";
const EQUIP_COLOR = "#888";
const PLATE_COLOR = "#C62828";

function drawHead(ctx, cx, cy, r = 18) {
  ctx.fillStyle = SKIN_COLOR;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fill();
  // eye dots
  ctx.fillStyle = "#333";
  ctx.beginPath(); ctx.arc(cx - 5, cy - 2, 2, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(cx + 5, cy - 2, 2, 0, Math.PI * 2); ctx.fill();
}

function drawTorso(ctx, x1, y1, x2, y2) {
  ctx.strokeStyle = BODY_COLOR; ctx.lineWidth = 10; ctx.lineCap = "round";
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
}

function drawLimb(ctx, x1, y1, x2, y2, color = BODY_COLOR, w = 8) {
  ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = "round";
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
}

function drawJoint(ctx, cx, cy, r = 5) {
  ctx.fillStyle = BODY_COLOR;
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
}

function drawBar(ctx, x, y, w = 180, h = 12) {
  // shaft
  ctx.fillStyle = EQUIP_COLOR; ctx.fillRect(x, y, w, h);
  // shine
  ctx.fillStyle = "#bbb"; ctx.fillRect(x + 6, y + 2, w - 12, h * 0.4);
  // plates
  ctx.fillStyle = PLATE_COLOR;
  ctx.fillRect(x - 10, y - 5, 12, h + 10);
  ctx.fillRect(x + w - 2, y - 5, 12, h + 10);
  ctx.fillStyle = "#a00";
  ctx.fillRect(x - 8, y - 3, 8, h + 6);
  ctx.fillRect(x + w, y - 3, 8, h + 6);
}

function drawDumbbell(ctx, x, y) {
  ctx.fillStyle = EQUIP_COLOR; ctx.fillRect(x, y, 26, 8);
  ctx.fillStyle = "#555";
  ctx.fillRect(x - 5, y - 4, 7, 16);
  ctx.fillRect(x + 24, y - 4, 7, 16);
}

function drawGround(ctx, cx, y, spread = 130) {
  ctx.strokeStyle = "#ffffff14"; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.moveTo(cx - spread, y); ctx.lineTo(cx + spread, y); ctx.stroke();
}

/* Full standing body (straight up) */
function standingBody(ctx, cx, headY, neckY, waistY, kneeY, footY) {
  drawHead(ctx, cx, headY - 14);
  drawLimb(ctx, cx, neckY, cx, waistY, BODY_COLOR, 10); // torso
  // shoulders visual
  drawLimb(ctx, cx - 40, neckY + 8, cx + 40, neckY + 8, BODY_COLOR, 6);
  // legs
  drawLimb(ctx, cx, waistY, cx - 26, kneeY, BODY_COLOR, 9);
  drawLimb(ctx, cx, waistY, cx + 26, kneeY, BODY_COLOR, 9);
  drawJoint(ctx, cx - 26, kneeY);
  drawJoint(ctx, cx + 26, kneeY);
  drawLimb(ctx, cx - 26, kneeY, cx - 20, footY, BODY_COLOR, 8);
  drawLimb(ctx, cx + 26, kneeY, cx + 20, footY, BODY_COLOR, 8);
  // feet
  drawLimb(ctx, cx - 20, footY, cx - 32, footY + 4, BODY_COLOR, 6);
  drawLimb(ctx, cx + 20, footY, cx + 32, footY + 4, BODY_COLOR, 6);
}

/* Hinged body (for rows, RDL, deadlift) */
function hingedBody(ctx, cx, cy, hingeAngle) {
  const tx = Math.sin(hingeAngle) * 65;
  const ty = Math.cos(hingeAngle) * 65;
  const hx = cx - tx, hy = cy - ty;
  drawHead(ctx, hx, hy - 18);
  drawLimb(ctx, hx, hy, cx, cy, BODY_COLOR, 10);
  drawLimb(ctx, cx, cy, cx - 24, cy + 60, BODY_COLOR, 9);
  drawLimb(ctx, cx, cy, cx + 24, cy + 60, BODY_COLOR, 9);
  drawLimb(ctx, cx - 24, cy + 60, cx - 18, cy + 120, BODY_COLOR, 8);
  drawLimb(ctx, cx + 24, cy + 60, cx + 18, cy + 120, BODY_COLOR, 8);
  drawJoint(ctx, cx - 24, cy + 60);
  drawJoint(ctx, cx + 24, cy + 60);
  return { sx: hx, sy: hy }; // shoulder position
}

/* Lying body */
function lyingBody(ctx, cx, cy) {
  drawHead(ctx, cx - 100, cy - 3);
  drawLimb(ctx, cx - 80, cy, cx + 60, cy, BODY_COLOR, 10);
  drawLimb(ctx, cx + 60, cy, cx + 95, cy + 5, BODY_COLOR, 9);
  drawLimb(ctx, cx + 60, cy, cx + 92, cy - 5, BODY_COLOR, 9);
}

/* ── Individual Animation Functions ───────────────────────── */
/* Each receives: (t, ctx, W, H)
   t = time in seconds (continuous)
   Returns nothing; draws directly to ctx
*/

const ANIMATIONS = {

  /* ── CHEST & TRICEPS ──────────────────────────────────── */

  benchPress(t, ctx, W, H) {
    const s = Math.sin(t * 3);
    const cy = H * 0.5;
    const armAngle = 0.45 + s * 0.38;
    // bench
    ctx.fillStyle = "#2a2a3a";
    ctx.fillRect(W / 2 - 85, cy + 30, 170, 16);
    standingBody(ctx, W / 2, cy - 55, cy - 55, cy + 20, cy + 80, cy + 160);
    const lx = W / 2 - 52, rx = W / 2 + 52, ay = cy - 25;
    // left arm
    drawLimb(ctx, lx, ay, lx - 32 * Math.cos(armAngle), ay - 42 * Math.sin(armAngle), ARM_COLOR, 7);
    // right arm
    drawLimb(ctx, rx, ay, rx + 32 * Math.cos(armAngle), ay - 42 * Math.sin(armAngle), ARM_COLOR, 7);
    // bar
    const bx = W / 2 - 90, by = ay - 42 * Math.sin(armAngle) - 8;
    drawBar(ctx, bx, by, 180, 12);
  },

  inclinePress(t, ctx, W, H) {
    const s = Math.sin(t * 3);
    const cy = H * 0.5;
    const a = 0.52 + s * 0.32;
    // incline bench
    ctx.fillStyle = "#2a2a3a";
    ctx.fillRect(W / 2 - 70, cy + 20, 140, 14);
    ctx.fillRect(W / 2 - 50, cy - 40, 100, 70);
    standingBody(ctx, W / 2, cy - 55, cy - 55, cy + 18, cy + 70, cy + 145);
    const lx = W / 2 - 50, rx = W / 2 + 50, ay = cy - 45;
    drawLimb(ctx, lx, ay, lx - 30 * Math.cos(a), ay - 50 * Math.sin(a), ARM_COLOR, 7);
    drawLimb(ctx, rx, ay, rx + 30 * Math.cos(a), ay - 50 * Math.sin(a), ARM_COLOR, 7);
    drawDumbbell(ctx, lx - 30 * Math.cos(a) - 14, ay - 50 * Math.sin(a) - 6);
    drawDumbbell(ctx, rx + 30 * Math.cos(a) + 2,  ay - 50 * Math.sin(a) - 6);
  },

  cableFlye(t, ctx, W, H) {
    const s = Math.sin(t * 2.5);
    const cy = H * 0.44;
    const spread = 58 + s * 45;
    standingBody(ctx, W / 2, cy - 68, cy - 68, cy + 12, cy + 72, cy + 152);
    const sy = cy - 18;
    // cable lines
    ctx.strokeStyle = "#ffffff22"; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(0, cy - 80); ctx.lineTo(W / 2 - spread, sy + s * 18); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(W, cy - 80); ctx.lineTo(W / 2 + spread, sy + s * 18); ctx.stroke();
    drawLimb(ctx, W / 2, sy, W / 2 - spread, sy + s * 18, ARM_COLOR, 7);
    drawLimb(ctx, W / 2, sy, W / 2 + spread, sy + s * 18, ARM_COLOR, 7);
    // handles
    ctx.fillStyle = "#7F77DD";
    ctx.beginPath(); ctx.arc(W / 2 - spread, sy + s * 18, 6, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(W / 2 + spread, sy + s * 18, 6, 0, Math.PI * 2); ctx.fill();
  },

  pushdown(t, ctx, W, H) {
    const s = Math.sin(t * 3);
    const cy = H * 0.41;
    standingBody(ctx, W / 2, cy - 80, cy - 80, cy, cy + 60, cy + 140);
    const ey = cy - 10;
    const handY = ey + 48 + s * 32;
    // rope/cable
    ctx.strokeStyle = "#ffffff22"; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(W / 2, H * 0.02); ctx.lineTo(W / 2, ey); ctx.stroke();
    // forearms
    drawLimb(ctx, W / 2 - 22, ey, W / 2 - 22, handY, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 22, ey, W / 2 + 22, handY, ARM_COLOR, 7);
    drawBar(ctx, W / 2 - 36, handY - 4, 72, 9);
  },

  skullCrusher(t, ctx, W, H) {
    const s = Math.sin(t * 3);
    const cy = H * 0.52;
    const barAngle = Math.PI / 2 + s * 0.55;
    // bench
    ctx.fillStyle = "#2a2a3a"; ctx.fillRect(W / 2 - 90, cy + 20, 180, 15);
    standingBody(ctx, W / 2, cy - 58, cy - 58, cy + 22, cy + 78, cy + 158);
    const ex = W / 2 - 52, ey = cy - 22;
    const bLen = 55;
    drawLimb(ctx, ex, ey, ex + Math.cos(barAngle) * bLen, ey - Math.sin(barAngle) * bLen, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 52, ey, (W / 2 + 52) + Math.cos(Math.PI - barAngle) * bLen, ey - Math.sin(Math.PI - barAngle) * bLen, ARM_COLOR, 7);
    drawBar(ctx, ex + Math.cos(barAngle) * bLen - 52, ey - Math.sin(barAngle) * bLen - 7, 104, 10);
  },

  pushup(t, ctx, W, H) {
    const s = Math.sin(t * 3);
    const bodyY = H * 0.52 + s * 20;
    // body horizontal
    drawHead(ctx, W / 2 - 100, bodyY - 5);
    drawLimb(ctx, W / 2 - 82, bodyY, W / 2 + 65, bodyY, BODY_COLOR, 10);
    // arms
    drawLimb(ctx, W / 2 - 42, bodyY - 5, W / 2 - 80, bodyY + 28 - s * 18, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 42, bodyY - 5, W / 2 + 80, bodyY + 28 - s * 18, ARM_COLOR, 7);
    // legs
    drawLimb(ctx, W / 2 + 65, bodyY, W / 2 + 95, bodyY + 6, BODY_COLOR, 9);
    drawGround(ctx, W / 2, bodyY + 35);
  },

  /* ── BACK & BICEPS ────────────────────────────────────── */

  pullup(t, ctx, W, H) {
    const s = Math.sin(t * 2.5);
    const bodyY = H * 0.52 + s * 42;
    standingBody(ctx, W / 2, bodyY - 68, bodyY - 68, bodyY + 10, bodyY + 72, bodyY + 152);
    drawLimb(ctx, W / 2 - 52, bodyY - 48, W / 2 - 78, H * 0.14, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 52, bodyY - 48, W / 2 + 78, H * 0.14, ARM_COLOR, 7);
    // bar
    drawBar(ctx, W / 2 - 100, H * 0.10, 200, 14);
    // mounts
    ctx.strokeStyle = "#555"; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(W / 2 - 100, H * 0.10); ctx.lineTo(W / 2 - 100, H * 0.02); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(W / 2 + 100, H * 0.10); ctx.lineTo(W / 2 + 100, H * 0.02); ctx.stroke();
  },

  barbellRow(t, ctx, W, H) {
    const s = Math.sin(t * 3);
    const cy = H * 0.46;
    const hinge = 0.6;
    const { sx, sy } = hingedBody(ctx, W / 2, cy, hinge);
    const handY = cy + 48 - s * 28;
    drawLimb(ctx, sx - 12, sy + 12, W / 2 - 52, handY, ARM_COLOR, 7);
    drawLimb(ctx, sx + 12, sy + 12, W / 2 + 52, handY, ARM_COLOR, 7);
    drawBar(ctx, W / 2 - 78, handY + 4, 156, 10);
    drawGround(ctx, W / 2, cy + 125);
  },

  latPulldown(t, ctx, W, H) {
    const s = Math.sin(t * 2.5);
    const cy = H * 0.44;
    const barY = H * 0.08 + ((s + 1) / 2) * 62;
    standingBody(ctx, W / 2, cy - 74, cy - 74, cy + 6, cy + 66, cy + 146);
    drawLimb(ctx, W / 2 - 52, cy - 38, W / 2 - 80, barY + 8, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 52, cy - 38, W / 2 + 80, barY + 8, ARM_COLOR, 7);
    drawBar(ctx, W / 2 - 86, barY, 172, 10);
    ctx.strokeStyle = "#ffffff18"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(W / 2, H * 0.01); ctx.lineTo(W / 2, barY); ctx.stroke();
  },

  bicepCurl(t, ctx, W, H) {
    const s = Math.sin(t * 3);
    const cy = H * 0.41;
    const angle = 0.2 + ((s + 1) / 2) * 1.15;
    standingBody(ctx, W / 2, cy - 80, cy - 80, cy, cy + 60, cy + 140);
    const ex = W / 2 - 34, ey = cy + 14;
    drawLimb(ctx, ex, ey, ex - Math.cos(angle) * 55, ey - Math.sin(angle) * 55, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 34, ey, (W / 2 + 34) + Math.cos(angle) * 55, ey - Math.sin(angle) * 55, ARM_COLOR, 7);
    drawDumbbell(ctx, ex - Math.cos(angle) * 55 - 14, ey - Math.sin(angle) * 55 - 6);
    drawDumbbell(ctx, (W / 2 + 34) + Math.cos(angle) * 55 + 2, ey - Math.sin(angle) * 55 - 6);
  },

  hammerCurl(t, ctx, W, H) {
    // same motion, different grip emphasis
    ANIMATIONS.bicepCurl(t, ctx, W, H);
  },

  /* ── LEGS ─────────────────────────────────────────────── */

  squat(t, ctx, W, H) {
    const s = (Math.sin(t * 2.5) + 1) / 2;
    const hipDrop = s * 65;
    const kneeFlare = s * 18;
    const cy = H * 0.35;
    const headY = cy - hipDrop * 0.15;
    // body
    drawHead(ctx, W / 2, headY - 80);
    drawLimb(ctx, W / 2, headY - 62, W / 2, headY + hipDrop * 0.2, BODY_COLOR, 10);
    // thighs
    drawLimb(ctx, W / 2, headY + hipDrop * 0.2, W / 2 - 40 - kneeFlare, headY + hipDrop * 0.2 + 62, BODY_COLOR, 9);
    drawLimb(ctx, W / 2, headY + hipDrop * 0.2, W / 2 + 40 + kneeFlare, headY + hipDrop * 0.2 + 62, BODY_COLOR, 9);
    // shins
    drawLimb(ctx, W / 2 - 40 - kneeFlare, headY + hipDrop * 0.2 + 62, W / 2 - 28, headY + hipDrop * 0.2 + 130, BODY_COLOR, 8);
    drawLimb(ctx, W / 2 + 40 + kneeFlare, headY + hipDrop * 0.2 + 62, W / 2 + 28, headY + hipDrop * 0.2 + 130, BODY_COLOR, 8);
    drawJoint(ctx, W / 2 - 40 - kneeFlare, headY + hipDrop * 0.2 + 62);
    drawJoint(ctx, W / 2 + 40 + kneeFlare, headY + hipDrop * 0.2 + 62);
    // bar on back
    drawBar(ctx, W / 2 - 80, headY - 66, 160, 11);
    // arms holding bar
    drawLimb(ctx, W / 2 - 40, headY - 58, W / 2 - 78, headY - 58, ARM_COLOR, 6);
    drawLimb(ctx, W / 2 + 40, headY - 58, W / 2 + 78, headY - 58, ARM_COLOR, 6);
    drawGround(ctx, W / 2, headY + hipDrop * 0.2 + 136);
  },

  legPress(t, ctx, W, H) {
    const s = Math.sin(t * 2.5);
    const cy = H * 0.5;
    const legLen = 38 + ((s + 1) / 2) * 42;
    lyingBody(ctx, W / 2, cy);
    // legs
    drawLimb(ctx, W / 2 + 30, cy - 5, W / 2 + 30, cy - 5 - legLen, BODY_COLOR, 9);
    drawLimb(ctx, W / 2 + 60, cy - 5, W / 2 + 60, cy - 5 - legLen, BODY_COLOR, 9);
    drawLimb(ctx, W / 2 + 30, cy - 5 - legLen, W / 2 + 20, cy - 5 - legLen - 22, BODY_COLOR, 8);
    drawLimb(ctx, W / 2 + 60, cy - 5 - legLen, W / 2 + 50, cy - 5 - legLen - 22, BODY_COLOR, 8);
    // platform
    ctx.fillStyle = "#2a2a3a";
    ctx.fillRect(W / 2 - 10, cy - 5 - legLen - 30, 80, 24);
    ctx.fillStyle = "#444";
    ctx.fillRect(W / 2, cy - 5 - legLen - 26, 60, 16);
  },

  rdl(t, ctx, W, H) {
    const s = (Math.sin(t * 2.5) + 1) / 2;
    const cy = H * 0.42;
    const hingeAngle = s * 0.72;
    const { sx, sy } = hingedBody(ctx, W / 2, cy, hingeAngle);
    const handY = cy + 80 * Math.sin(hingeAngle) + 38;
    drawLimb(ctx, sx - 12, sy + 10, W / 2 - 52, handY, ARM_COLOR, 7);
    drawLimb(ctx, sx + 12, sy + 10, W / 2 + 52, handY, ARM_COLOR, 7);
    drawBar(ctx, W / 2 - 80, handY - 2, 160, 11);
    drawGround(ctx, W / 2, cy + 125);
  },

  legCurl(t, ctx, W, H) {
    const s = (Math.sin(t * 3) + 1) / 2;
    const cy = H * 0.48;
    lyingBody(ctx, W / 2, cy);
    const angle = s * 1.25;
    // legs curling up
    drawLimb(ctx, W / 2 + 30, cy + 10, W / 2 + 30 - Math.sin(angle) * 52, cy + 10 - Math.cos(angle) * 52, BODY_COLOR, 9);
    drawLimb(ctx, W / 2 + 60, cy + 10, W / 2 + 60 - Math.sin(angle) * 52, cy + 10 - Math.cos(angle) * 52, BODY_COLOR, 9);
    // pad
    ctx.fillStyle = "#7F77DD44";
    ctx.fillRect(W / 2 + 30 - Math.sin(angle) * 52 - 10, cy + 10 - Math.cos(angle) * 52 - 10, 45, 14);
  },

  calfRaise(t, ctx, W, H) {
    const s = Math.sin(t * 3.5);
    const rise = ((s + 1) / 2) * 26;
    const cy = H * 0.30 - rise;
    standingBody(ctx, W / 2, cy - 82, cy - 82, cy, cy + 65, cy + 130);
    drawGround(ctx, W / 2, cy + 135);
    // heel rise visual emphasis
    ctx.fillStyle = "#7F77DD33";
    ctx.fillRect(W / 2 - 40, cy + 125, 80, rise + 8);
  },

  /* ── SHOULDERS ────────────────────────────────────────── */

  ohp(t, ctx, W, H) {
    const s = Math.sin(t * 2.5);
    const cy = H * 0.41;
    const barY = cy - 82 - ((s + 1) / 2) * 58;
    standingBody(ctx, W / 2, cy - 82, cy - 82, cy, cy + 60, cy + 140);
    drawLimb(ctx, W / 2 - 52, cy - 30, W / 2 - 64, barY + 8, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 52, cy - 30, W / 2 + 64, barY + 8, ARM_COLOR, 7);
    drawBar(ctx, W / 2 - 80, barY, 160, 11);
  },

  lateralRaise(t, ctx, W, H) {
    const s = (Math.sin(t * 2.5) + 1) / 2;
    const cy = H * 0.41;
    const spread = s * 82;
    standingBody(ctx, W / 2, cy - 82, cy - 82, cy, cy + 60, cy + 140);
    const sy = cy - 14;
    drawLimb(ctx, W / 2 - 38, sy, W / 2 - 38 - spread, sy - spread * 0.42, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 38, sy, W / 2 + 38 + spread, sy - spread * 0.42, ARM_COLOR, 7);
    drawDumbbell(ctx, W / 2 - 38 - spread - 14, sy - spread * 0.42 - 5);
    drawDumbbell(ctx, W / 2 + 38 + spread + 2,  sy - spread * 0.42 - 5);
  },

  frontRaise(t, ctx, W, H) {
    const s = (Math.sin(t * 2.5) + 1) / 2;
    const cy = H * 0.41;
    const lift = s * 85;
    standingBody(ctx, W / 2, cy - 82, cy - 82, cy, cy + 60, cy + 140);
    drawLimb(ctx, W / 2 - 36, cy - 10, W / 2 - 55, cy - 10 - lift, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 36, cy - 10, W / 2 + 55, cy - 10 - lift, ARM_COLOR, 7);
    drawDumbbell(ctx, W / 2 - 68, cy - 10 - lift - 5);
    drawDumbbell(ctx, W / 2 + 55, cy - 10 - lift - 5);
  },

  facePull(t, ctx, W, H) {
    const s = Math.sin(t * 2.5);
    const cy = H * 0.41;
    const pullX = 52 + s * 32;
    standingBody(ctx, W / 2, cy - 82, cy - 82, cy, cy + 60, cy + 140);
    const hy = cy - 55 - s * 10;
    drawLimb(ctx, W / 2 - 36, cy - 20, W / 2 - pullX, hy, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 36, cy - 20, W / 2 + pullX, hy, ARM_COLOR, 7);
    // cable lines
    ctx.strokeStyle = "#ffffff18"; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(W + 10, cy - 60); ctx.lineTo(W / 2 + pullX, hy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(W + 10, cy - 60); ctx.lineTo(W / 2 - pullX, hy); ctx.stroke();
  },

  shrug(t, ctx, W, H) {
    const s = Math.sin(t * 4.5);
    const rise = ((s + 1) / 2) * 14;
    const cy = H * 0.37 - rise;
    standingBody(ctx, W / 2, cy - 82, cy - 82, cy, cy + 60, cy + 140);
    drawLimb(ctx, W / 2 - 48, cy - 5 + rise, W / 2 - 52, cy + 52, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 48, cy - 5 + rise, W / 2 + 52, cy + 52, ARM_COLOR, 7);
    drawDumbbell(ctx, W / 2 - 66, cy + 50);
    drawDumbbell(ctx, W / 2 + 54, cy + 50);
    // shoulder rise shadow
    ctx.fillStyle = "#7F77DD22";
    ctx.fillRect(W / 2 - 55, cy - 20, 110, rise + 10);
  },

  /* ── FULL BODY / CORE ─────────────────────────────────── */

  deadlift(t, ctx, W, H) {
    const s = (Math.sin(t * 2) + 1) / 2;
    const hingeAngle = (1 - s) * 0.78;
    const cy = H * (0.56 - s * 0.16);
    const { sx, sy } = hingedBody(ctx, W / 2, cy, hingeAngle);
    const handY = cy + 70 * Math.sin(hingeAngle) + (1 - s) * 42;
    drawLimb(ctx, sx - 14, sy + 8, W / 2 - 52, handY, ARM_COLOR, 7);
    drawLimb(ctx, sx + 14, sy + 8, W / 2 + 52, handY, ARM_COLOR, 7);
    drawBar(ctx, W / 2 - 90, handY - 2, 180, 12);
    drawGround(ctx, W / 2, cy + 126);
  },

  plank(t, ctx, W, H) {
    const wobble = Math.sin(t * 7) * 2.5;
    const cy = H * 0.52;
    // body horizontal with slight core emphasis
    drawHead(ctx, W / 2 - 102, cy - 4 + wobble * 0.3);
    drawLimb(ctx, W / 2 - 84, cy + wobble, W / 2 + 62, cy + wobble, BODY_COLOR, 11);
    // forearms on ground
    drawLimb(ctx, W / 2 - 55, cy + wobble, W / 2 - 68, cy + 42, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 22, cy + wobble, W / 2 + 35, cy + 42, ARM_COLOR, 7);
    // feet
    drawLimb(ctx, W / 2 + 62, cy + wobble, W / 2 + 82, cy + 6, BODY_COLOR, 9);
    // core highlight
    ctx.fillStyle = "#7F77DD18";
    ctx.fillRect(W / 2 - 70, cy - 14 + wobble, 140, 32);
    drawGround(ctx, W / 2, cy + 46);
  },

  run(t, ctx, W, H) {
    const cy = H * 0.36;
    const legA = Math.sin(t * 4.2) * 0.72;
    const armA = Math.sin(t * 4.2 + Math.PI) * 0.52;
    drawHead(ctx, W / 2, cy - 82);
    drawLimb(ctx, W / 2, cy - 64, W / 2, cy, BODY_COLOR, 10);
    // arms
    drawLimb(ctx, W / 2 - 38, cy - 42, W / 2 - 38 - Math.cos(armA) * 46, cy - 42 - Math.sin(armA) * 38, ARM_COLOR, 7);
    drawLimb(ctx, W / 2 + 38, cy - 42, W / 2 + 38 + Math.cos(-armA) * 46, cy - 42 - Math.sin(-armA) * 38, ARM_COLOR, 7);
    // legs
    const lKneeX = W / 2 - 24 + Math.sin(legA) * 40;
    const lKneeY = cy + 60 - Math.abs(Math.cos(legA)) * 20;
    drawLimb(ctx, W / 2 - 24, cy, lKneeX, lKneeY, BODY_COLOR, 9);
    drawLimb(ctx, lKneeX, lKneeY, lKneeX + Math.sin(legA) * 18, lKneeY + 50, BODY_COLOR, 8);
    drawJoint(ctx, lKneeX, lKneeY);
    const rKneeX = W / 2 + 24 + Math.sin(-legA) * 40;
    const rKneeY = cy + 60 - Math.abs(Math.cos(legA)) * 20;
    drawLimb(ctx, W / 2 + 24, cy, rKneeX, rKneeY, BODY_COLOR, 9);
    drawLimb(ctx, rKneeX, rKneeY, rKneeX + Math.sin(-legA) * 18, rKneeY + 50, BODY_COLOR, 8);
    drawJoint(ctx, rKneeX, rKneeY);
    drawGround(ctx, W / 2, cy + 114);
  }
};

/* ── UI Rendering ──────────────────────────────────────────── */

let animFrame = null;
let activeGoal = null;
let activeEx   = null;

function renderGoals() {
  const el = document.getElementById("goals");
  el.innerHTML = "";
  Object.keys(DATA).forEach(g => {
    const b = document.createElement("button");
    b.className = "goal-btn" + (activeGoal === g ? " active" : "");
    b.textContent = DATA[g].icon + "  " + g;
    b.onclick = () => {
      activeGoal = g;
      activeEx   = null;
      renderGoals();
      renderExList();
      showEmpty();
    };
    el.appendChild(b);
  });
}

function renderExList() {
  const el = document.getElementById("exList");
  el.innerHTML = "";
  if (!activeGoal) return;
  Object.keys(DATA[activeGoal].exercises).forEach(ex => {
    const b = document.createElement("button");
    b.className = "ex-btn" + (activeEx === ex ? " active" : "");
    b.textContent = ex;
    b.onclick = () => {
      activeEx = ex;
      renderExList();
      startAnim(activeGoal, ex);
    };
    el.appendChild(b);
  });
}

function showEmpty() {
  document.getElementById("viewer").innerHTML = `
    <div class="empty-state">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
        <circle cx="24" cy="9" r="6" fill="#AFA9EC"/>
        <rect x="19" y="16" width="10" height="16" rx="4" fill="#AFA9EC"/>
        <rect x="9"  y="17" width="8"  height="13" rx="3" fill="#AFA9EC"/>
        <rect x="31" y="17" width="8"  height="13" rx="3" fill="#AFA9EC"/>
        <rect x="16" y="33" width="7"  height="14" rx="3" fill="#AFA9EC"/>
        <rect x="25" y="33" width="7"  height="14" rx="3" fill="#AFA9EC"/>
      </svg>
      <span>Pick an exercise to animate</span>
    </div>`;
}

function startAnim(goal, exName) {
  if (animFrame) cancelAnimationFrame(animFrame);

  const ex     = DATA[goal].exercises[exName];
  const animFn = ANIMATIONS[ex.anim];
  const viewer = document.getElementById("viewer");

  viewer.innerHTML = `
    <div class="viewer-title">${exName}</div>
    <span class="viewer-tag">${goal}</span>
    <div class="muscle-tags">
      ${ex.muscles.map(m => `<span class="muscle-tag">${m}</span>`).join("")}
    </div>
    <canvas id="animCanvas" width="400" height="290"></canvas>
    <div class="phase-bar">
      ${ex.phases.map((ph, i) => `<span class="phase" id="ph${i}">${ph}</span>`).join("")}
    </div>
    <p class="tips">💡 ${ex.tips}</p>
  `;

  const canvas = document.getElementById("animCanvas");
  const ctx    = canvas.getContext("2d");
  const W = 400, H = 290;
  let t = 0;

  function loop() {
    t += 0.032;
    ctx.clearRect(0, 0, W, H);

    // phase indicator
    const p   = Math.sin(t * 2.5);
    const idx = Math.min(Math.floor(((p + 1) / 2) * ex.phases.length), ex.phases.length - 1);
    ex.phases.forEach((_, i) => {
      const el = document.getElementById("ph" + i);
      if (el) el.className = "phase" + (i === idx ? " active" : "");
    });

    animFn(t, ctx, W, H);
    animFrame = requestAnimationFrame(loop);
  }

  loop();
}

/* ── Init ──────────────────────────────────────────────────── */
renderGoals();
renderExList();