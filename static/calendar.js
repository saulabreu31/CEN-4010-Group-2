document.addEventListener('DOMContentLoaded', () => {
    const eventList = document.getElementById('event-list');
    const addEventForm = document.getElementById('add-event-form');

    // Fetch and display events
    const loadEvents = async () => {
        const response = await fetch('/calendar/events?user_id=1'); // Example user_id
        const events = await response.json();
        eventList.innerHTML = '';
        events.forEach(event => {
            const listItem = document.createElement('li');
            listItem.textContent = `${event.title} - ${event.start_time} to ${event.end_time}`;
            eventList.appendChild(listItem);
        });
    };

    // Add event
    addEventForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            user_id: 1, // Example user_id
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            start_time: document.getElementById('start_time').value,
            end_time: document.getElementById('end_time').value,
        };
        await fetch('/calendar/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        addEventForm.reset();
        loadEvents();
    });

    loadEvents();
});
