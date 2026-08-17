document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('playersTable');
    const tbody = table.querySelector('tbody');
    const headers = table.querySelectorAll('th');
    let currentSort = { key: 'name', asc: true };

    function sortTable(key, type, asc) {
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((a,b) => {
            const aVal = a.querySelector(`td[data-key="${key}"]`).dataset.value;
            const bVal = b.querySelector(`td[data-key="${key}"]`).dataset.value;
            if (type === 'number') {
                return asc ? aVal - bVal : bVal - aVal;
            }
            return asc ? aVal.localeCompare(bVal, 'pt-BR') : bVal.localeCompare(aVal, 'pt-BR');  
        });
        rows.forEach(row => tbody.appendChild(row));
        updateHeaderIndicators(key, asc);
    }

    function updateHeaderIndicators(activeKey, asc) {
        headers.forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
            if(th.dataset.key === activeKey) {
                th.classList.add(asc ? 'sort-asc' : 'sort-desc');
            }
        });
    }

    headers.forEach(th => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            const key = th.dataset.key;
            const type = th.dataset.type;
            const asc = currentSort.key === key ? !currentSort.asc : (type === 'string');
            currentSort = { key, asc };
            sortTable(key, type, asc);
        });
    });

    sortTable('name', 'string', true);
});

document.addEventListener('DOMContentLoaded', function () {
    const bigPhoto = document.getElementById('big-player-photo');
    const bigName = document.getElementById('big-player-name');
    const bigNickname = document.getElementById('big-player-nickname');

    const captainData = {
        photo: bigPhoto.src,
        name: bigName.textContent,
        nickname: bigNickname.textContent
    };

    function setBigPlayer(name, nickname, photo, isCaptain) {
        bigPhoto.src = photo;
        bigName.textContent = isCaptain ? name + ' (C)' : name;
        bigNickname.textContent = nickname;
    }

    setBigPlayer(captainData.name, captainData.nickname, captainData.photo, true);

    document.querySelectorAll('.player').forEach(function (player) {
        player.addEventListener('mouseenter', function () {
            const isCaptain = player.dataset.captain === '1';
            setBigPlayer(player.dataset.name, player.dataset.nickname, player.dataset.photo, isCaptain);
        });
    });
});


































function abrirModal(matchId) {
    const data = matchDetails[matchId];
    if (!data) return;

    // Jogador Destaque da Partida
    let potmHtml = "<p>Nenhum jogador destaque definido</p>";
    if (data.player_of_the_match) {
        const potm = data.player_of_the_match;
        potmHtml = /*html*/`
            <div class="potm">
                <img src="${potm.photo}" class="potm-photo">
                <p>⭐ Destaque: <strong>${potm.name}</strong> (${potm.nickname}) ${potm.is_captain ? "(C)" : ""}</p>
                ${potm.was_round_player ? "<p>Também foi Jogador da Rodada</p>" : ""}
            </div>
        `;
    }

    // Jogadores de cada time (recebe a lista já separada)
    function renderPlayers(players) {
        if (players.length === 0) return "<p>W.O.</p>";
        return players.map(p => /*html*/`
            <div class="modal-player">
                <div class="modal-player-photo-wrapper">
                    <img src="${p.photo}" class="modal-player-photo">
                </div>
                <p>${p.name} ${p.is_captain ? "(C)" : ""}</p>
                <p>${p.nickname}</p>
                ${p.round_selected ? "<span>⭐</span>" : ""}
            </div>
        `).join("");
    }

    // Separa gols por time, usando o nome do time como comparação
    const homeGoals = data.goals.filter(g => g.team_name === data.home_team_name);
    const awayGoals = data.goals.filter(g => g.team_name === data.away_team_name);

    function renderGoals(goals) {
        if (goals.length === 0) return "";
        return goals.map(g => /*html*/` 
            <div class="modal-player">
                <div class="modal-player-photo-wrapper">
                    <img src="${g.photo}" class="modal-player-photo">
                </div>
                <div class="modal-goal">${g.player_name}${g.own_goal ? " (gc) " : ""} ⚽</div>
            </div>
        `).join("");
    }

    // Separa assistências por time
    const homeAssists = data.assists.filter(a => a.team_name === data.home_team_name);
    const awayAssists = data.assists.filter(a => a.team_name === data.away_team_name);

    function renderAssists(assists) {
        if (assists.length === 0) return "";
        return assists.map(a => /*html*/`
            <div class="modal-assist">🅰️ ${a.player_name}</div>
        `).join("");
    }

    // Separa cartões por time
    const homeCards = data.cards.filter(c => c.team_name === data.home_team_name);
    const awayCards = data.cards.filter(c => c.team_name === data.away_team_name);

    function renderCards(cards) {
        if (cards.length === 0) return "";
        return cards.map(c => `<div class="modal-cards">${c.card_type === "yellow" ? "🟨" : "🟥"} ${c.player_name}</div>`).join("");
    }

    document.getElementById('modalHeader').innerHTML = /*html*/`
        <div class="match-card">
            <div class="home-team">
                <p class="home-team-name">${ data.home_team_name }</p>
                <img src="/static/images/Team_badges/${data.home_team_badge}" class="home-team-badge">
            </div>
            <div class="match-score">
                <p class="score">${ data.home_team_goals } - ${ data.away_team_goals }</p>
            </div>
            <div class="away-team">
                <img src="/static/images/Team_badges/${data.away_team_badge}" class="away-team-badge">
                <p class="away-team-name">${ data.away_team_name }</p>
            </div>
        </div>
    `;


    document.getElementById('modalBody').innerHTML = /*html*/`
        <p>${data.date} às ${data.time}</p>
        <p>📍${data.location}</p>

        <div class="match-stats">
            <h5>Gols</h5>
            <div class="match-goals">
                <div class="home-goals">${renderGoals(homeGoals)}</div>
                <div class="away-goals">${renderGoals(awayGoals)}</div>
            </div>
            <h5>Assistências</h5>
            <div class="match-assists">
                <div class="home-assists">${renderAssists(homeAssists)}</div>
                <div class="away-assists">${renderAssists(awayAssists)}</div>
            </div>
            <h5>Cartões</h5>
            <div class="match-cards">
                <div class="home-cards">${renderCards(homeCards)}</div>
                <div class="away-cards">${renderCards(awayCards)}</div>
            </div>
            <div class="match-squad">
                <details>
                    <summary>Elenco ${data.home_team_name}</summary>
                    <div class="modal-team-players">${renderPlayers(data.home_players)}</div>
                </details>
                <details>
                    <summary>Elenco ${data.away_team_name}</summary>
                    <div class="modal-team-players">${renderPlayers(data.away_players)}</div>
                </details>
            </div>
        </div>

        <div class="player-of-the-match">${potmHtml}</div>
    `;

    document.getElementById('matchModal').style.display = "flex";
}






































function fecharModal() {
    document.getElementById('matchModal').style.display = "none";
}

function fecharModalFora(event) {
    if (event.target.id === 'matchModal') {
        fecharModal();
    }
}