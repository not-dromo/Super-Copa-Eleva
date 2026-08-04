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