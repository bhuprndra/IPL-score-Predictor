const form = document.getElementById('predict-form');
const btn = document.getElementById('submit-btn');
const errBox = document.getElementById('error-box');
const resSection = document.getElementById('result-section');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Reset UI state
  errBox.style.display = 'none';
  resSection.style.display = 'none';
  btn.classList.add('loading');
  btn.disabled = true;

  // ── Collect all form values ─
  // NOTE: field names here must match the keys app.py reads from request JSON
  const payload = {
    batting_team: document.getElementById('batting_team').value,
    bowling_team: document.getElementById('bowling_team').value,
    venue: document.getElementById('venue').value,
    runs: parseInt(document.getElementById('runs').value),
    overs: parseFloat(document.getElementById('overs').value),
    wickets: parseInt(document.getElementById('wickets').value),
    runs_last5: parseInt(document.getElementById('runs_last5').value),
    wickets_last5: parseInt(document.getElementById('wickets_last5').value)
  };

  // ── Client-side validation 
  if (!payload.batting_team || !payload.bowling_team || !payload.venue) {
    showError('Please select batting team, bowling team and city.');
    return;
  }
  if (payload.batting_team === payload.bowling_team) {
    showError('Batting team and bowling team cannot be the same.');
    return;
  }
  if (isNaN(payload.overs) || payload.overs < 0.1 || payload.overs > 19.5) {
    showError('Overs must be between 0.1 and 19.5');
    return;
  }
  if (isNaN(payload.runs) || payload.runs < 0) {
    showError('Runs scored cannot be negative.');
    return;
  }
  if (isNaN(payload.wickets) || payload.wickets < 0 || payload.wickets > 9) {
    showError('Wickets must be between 0 and 9.');
    return;
  }

  // ── Call Flask backend 
  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.error || 'Prediction failed');

    // ── Render result 
    document.getElementById('result-vs').innerHTML =
      `<span class="team-badge">🏏 ${payload.batting_team}</span>
       &nbsp;vs&nbsp;
       <span class="team-badge">🎯 ${payload.bowling_team}</span>`;

    document.getElementById('result-score').textContent = data.predicted_score;
    document.getElementById('result-range').textContent = data.score_range;

    const crr = data.crr ?? (payload.runs / payload.overs).toFixed(2);
    const rrr = data.rrr ?? '—';
    const totalBalls = 120;

    const oversPart = Math.floor(payload.overs);
    const ballsPart = Math.round((payload.overs - oversPart) * 10);

    const ballsBowled = oversPart * 6 + ballsPart;
    const ballsLeft = totalBalls - ballsBowled;

    const remOvers = Math.floor(ballsLeft / 6);
    const remBalls = ballsLeft % 6;

    const rem = `${remOvers}.${remBalls}`;
    const wrem = data.wickets_remaining ?? (10 - payload.wickets);

    document.getElementById('mini-stats').innerHTML = `
      <div class="mini-stat">
        <div class="mini-stat-val">${payload.runs}</div>
        <div class="mini-stat-lbl">Runs so far</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-val">${payload.wickets}</div>
        <div class="mini-stat-lbl">Wickets lost</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-val">${crr}</div>
        <div class="mini-stat-lbl">Current RR</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-val">${rrr}</div>
        <div class="mini-stat-lbl">Req. RR</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-val">${rem}</div>
        <div class="mini-stat-lbl">Overs left</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-val">${wrem}</div>
        <div class="mini-stat-lbl">Wickets left</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-val">${payload.runs_last5}</div>
        <div class="mini-stat-lbl">Runs last 5</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-val">${data.lower}–${data.upper}</div>
        <div class="mini-stat-lbl">Score range</div>
      </div>
    `;

    resSection.style.display = 'block';
    resSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    showError(err.message);
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
});

// ── Helper 
function showError(msg) {
  errBox.textContent = '⚠️ ' + msg;
  errBox.style.display = 'block';
  btn.classList.remove('loading');
  btn.disabled = false;
}
