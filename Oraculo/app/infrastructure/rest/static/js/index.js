// Function to fetch and append new items
function fetchAndAppendItems() {
    fetch('/api/get_packages')  // Fetch data from the Flask route
        .then(response => response.json())
        .then(data => {
            if(Object.keys(data).length === 0) return 
            // Clear the existing list
            const itemList = document.getElementById('itemList');
            itemList.innerHTML = '';

            console.log(data)

            // Append the new items to the list
            data.forEach(item => {
                const listItem = document.createElement('li');
                const h3 = document.createElement('h3');
                const p1 = document.createElement('p');
                const p2 = document.createElement('p');

                listItem.style.setProperty('--i', 2);

                h3.textContent = `Tráfego malicioso detectado`;
                p1.textContent = `IP de origem: ${item.ip}`;
                p2.textContent = `Tipo de ataque: ${item.attack_type}`;

                listItem.appendChild(h3);
                listItem.appendChild(p1);
                listItem.appendChild(p2);
                itemList.appendChild(listItem);
            });
            // data.forEach(item => {
            //     const listItem = document.createElement('li');
            //     const h3 = document.createElement('h3');
            //     const p = document.createElement('p');

            //     listItem.style.setProperty('--i', 2);

            //     h3.textContent = 'Tráfego malicioso';
            //     p.textContent = `O IP de origem ${item} foi bloqueado. Verifique a criação da regra de bloqueio no Firewall.`;

            //     listItem.appendChild(h3);
            //     listItem.appendChild(p);
            //     itemList.appendChild(listItem);
            // });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}