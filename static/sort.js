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
        potmHtml = `
            <div class="potm">
                <img src="${potm.photo}" class="potm-photo">
                <p>${potm.name} ${potm.is_captain ? "(C)" : ""}</p>
                <p>${potm.nickname}</p>
                ${potm.was_round_player ? "<p>Também foi Jogador da Rodada</p>" : ""}
            </div>
        `;
    }

    // Jogadores de cada time
    function renderPlayers(players) {
        if (players.length === 0) return "<p>Nenhum jogador registrado</p>";
        return players.map(p => `
            <div class="modal-player">
                <img src="${p.photo}" class="modal-player-photo">
                <p>${p.name} ${p.is_captain ? "(C)" : ""}</p>
                <p>${p.nickname}</p>
                ${p.round_selected ? "<span>⭐ Seleção da Rodada</span>" : ""}
            </div>
        `).join("");
    }

    // Gols
    let goalsHtml = "<p>Nenhum gol na partida</p>";
    if (data.goals.length > 0) {
        goalsHtml = data.goals.map(g => `
            <p>⚽ ${g.player_name} (${g.team_name})${g.own_goal ? " - contra" : ""}</p>
        `).join("");
    }

    // Assistências
    let assistsHtml = "<p>Nenhuma assistência na partida</p>";
    if (data.assists.length > 0) {
        assistsHtml = data.assists.map(a => `
            <p>🅰️ ${a.player_name} (${a.team_name})</p>
        `).join("");
    }

    // Cartões
    let cardsHtml = "<p>Nenhum cartão na partida</p>";
    if (data.cards.length > 0) {
        cardsHtml = data.cards.map(c => `
            <p>${c.card_type === "yellow" ? "🟨" : "🟥"} ${c.player_name} (${c.team_name})</p>
        `).join("");
    }

    document.getElementById('modalBody').innerHTML = `
        <h3>${data.home_team_name} ${data.home_team_goals} - ${data.away_team_goals} ${data.away_team_name}</h3>
        <p>${data.date} às ${data.time}</p>
        <p>${data.location}</p>

        <h4>Jogador Destaque</h4>
        ${potmHtml}

        <h4>${data.home_team_name}</h4>
        <div class="modal-team-players">${renderPlayers(data.home_players)}</div>

        <h4>${data.away_team_name}</h4>
        <div class="modal-team-players">${renderPlayers(data.away_players)}</div>

        <h4>Gols</h4>
        ${goalsHtml}

        <h4>Assistências</h4>
        ${assistsHtml}

        <h4>Cartões</h4>
        ${cardsHtml}
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