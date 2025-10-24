// ======================================================
// ⚙️ CONFIGURATION
// ======================================================

// 🔸 Địa chỉ FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000";

// API endpoint ở footer
document.addEventListener("DOMContentLoaded", () => {
  const footer = document.querySelector("footer p");
  footer.innerHTML += `<br><small style="color:#bbb;">Connected to API: <span style="color:#66ccff;">${API_BASE_URL}</span></small>`;
});

// =======================
// DOM Elements
// =======================
const playersTableBody = document.getElementById('players-table-body');
const playerForm = document.getElementById('player-form');
const matchesContainer = document.getElementById('matches-container');
const matchSelect = document.getElementById('match-select');
const statsDisplay = document.getElementById('stats-display');

// =======================
// Helper Functions
// =======================
function showMessage(container, message) {
  container.innerHTML = `<p class="no-data-msg">${message}</p>`;
}

function createStatCard(label, value) {
  const div = document.createElement('div');
  div.classList.add('stat-card');
  div.innerHTML = `<h4>${label}</h4><p>${value}</p>`;
  return div;
}

// =======================
// Player Management
// =======================
async function loadPlayers() {
  try {
    const res = await fetch(`${API_BASE_URL}/players/`);
    const data = await res.json();
    playersTableBody.innerHTML = '';

    if (data.length === 0) {
      showMessage(playersTableBody, "No players found.");
      return;
    }

    data.forEach(p => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${p.id}</td>
        <td>${p.name}</td>
        <td>${p.age}</td>
        <td>${p.position}</td>
        <td>${p.jersey_number}</td>
        <td>${p.injury_status}</td>
      `;
      playersTableBody.appendChild(row);
    });
  } catch (err) {
    console.error(err);
    showMessage(playersTableBody, "Error loading players.");
  }
}

playerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const player = {
    name: document.getElementById('player-name').value,
    age: parseInt(document.getElementById('player-age').value),
    date_of_birth: document.getElementById('player-dob').value,
    position: document.getElementById('player-position').value,
    jersey_number: parseInt(document.getElementById('player-number').value),
    transfer_price_vnd: 0,
    injury_status: "FIT"
  };

  try {
    const res = await fetch(`${API_BASE_URL}/players/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(player)
    });
    if (!res.ok) throw new Error("Failed to create player");
    await loadPlayers();
    playerForm.reset();
  } catch (err) {
    alert("Error adding player: " + err.message);
  }
});

// =======================
// Match Management
// =======================
async function loadMatches() {
  try {
    const res = await fetch(`${API_BASE_URL}/matches/upcoming`);
    const matches = await res.json();
    matchesContainer.innerHTML = '';
    matchSelect.innerHTML = `<option value="">-- Select a Completed Match --</option>`;

    if (matches.length === 0) {
      showMessage(matchesContainer, "No matches found.");
      return;
    }

    matches.forEach(m => {
      const matchCard = document.createElement('div');
      matchCard.classList.add('match-card', m.is_completed ? 'past' : 'upcoming');
      const statusText = m.is_completed ? 'Completed' : 'Scheduled';
      const score = m.is_completed ? `${m.our_score} - ${m.opponent_score}` : 'vs';
      matchCard.innerHTML = `
        <h4>${m.opponent_name}</h4>
        <p><strong>Date:</strong> ${m.match_date}</p>
        <p><strong>Venue:</strong> ${m.venue}</p>
        <p><strong>Status:</strong> ${statusText}</p>
        <p><strong>Score:</strong> ${score}</p>
      `;
      matchesContainer.appendChild(matchCard);

      if (m.is_completed) {
        const opt = document.createElement('option');
        opt.value = m.id;
        opt.textContent = `${m.match_date} vs ${m.opponent_name}`;
        matchSelect.appendChild(opt);
      }
    });
  } catch (err) {
    console.error(err);
    showMessage(matchesContainer, "Error loading matches.");
  }
}

// =======================
// Statistics
// =======================
async function loadMatchStats(matchId) {
  if (!matchId) {
    showMessage(statsDisplay, "Select a match to view statistics.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE_URL}/matches/${matchId}/stats`);
    if (!res.ok) throw new Error("Stats not found");
    const s = await res.json();
    statsDisplay.innerHTML = '';

    const stats = [
      ["Expected Goals (xG)", s.expected_goals],
      ["Shots on Target", s.shots_on_target],
      ["Ball Possession (%)", s.ball_possession_percent],
      ["Total Passes", s.total_passes],
      ["Successful Passes", s.successful_passes],
      ["Pass Success Rate (%)", s.pass_success_rate],
      ["Interceptions", s.interceptions],
      ["Successful Tackles", s.successful_tackles],
      ["Aerial Duels Won", s.aerial_disputes_won],
      ["Total Fouls", s.total_fouls],
      ["Yellow Cards", s.yellow_cards],
      ["Red Cards", s.red_cards]
    ];

    stats.forEach(([label, val]) => statsDisplay.appendChild(createStatCard(label, val)));
  } catch (err) {
    showMessage(statsDisplay, "No statistics available for this match.");
  }
}

matchSelect.addEventListener('change', (e) => {
  const matchId = e.target.value;
  loadMatchStats(matchId);
});

// =======================
// Initial Load
// =======================
document.addEventListener('DOMContentLoaded', () => {
  loadPlayers();
  loadMatches();
});
