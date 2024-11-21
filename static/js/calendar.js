document.addEventListener('DOMContentLoaded', () => {
   console.log('DOM Content Loaded');


   const eventForm = document.getElementById('event-form');
   const eventsList = document.getElementById('events-list');


   // Add error display element
   const errorDisplay = document.createElement('div');
   errorDisplay.id = 'error-display';
   errorDisplay.style.color = 'red';
   errorDisplay.style.marginBottom = '10px';
   eventForm.insertBefore(errorDisplay, eventForm.firstChild);


   function formatDate(dateString) {
       return new Date(dateString).toLocaleString();
   }


   function createEventElement(event) {
       const div = document.createElement('div');
       div.className = 'event-card';
       div.innerHTML = `
           <div class="event-title">${event.title}</div>
           <div class="event-description">${event.description || 'No description provided'}</div>
           <div class="event-time">Start: ${formatDate(event.start_time)}</div>
           <div class="event-time">End: ${formatDate(event.end_time)}</div>
           <button class="delete-event-btn" data-event-id="${event.id}">Delete</button>
       `;


       // Add event listener for delete button (same as before)
       div.querySelector('.delete-event-btn').addEventListener('click', async () => {
           try {
               const response = await fetch(`/calendar/delete/${event.id}`, {
                   method: 'DELETE'
               });


               const result = await response.json();


               if (result.success) {
                   div.remove();
                   alert('Event deleted successfully');
                   loadEvents();
               } else {
                   throw new Error(result.error || 'Failed to delete event');
               }
           } catch (error) {
               console.error('Error deleting event:', error);
               alert(`Error: ${error.message}`);
           }
       });


       return div;
   }


   function showError(message) {
       errorDisplay.textContent = message;
       setTimeout(() => {
           errorDisplay.textContent = '';
       }, 5000);
   }


   async function loadEvents() {
       console.log('Loading events...');
       try {
           const response = await fetch('/calendar/events?user_id=1');
           console.log('Events response:', response);


           if (!response.ok) {
               throw new Error(`HTTP error! status: ${response.status}`);
           }


           const data = await response.json();
           console.log('Fetched events:', data);


           eventsList.innerHTML = '';


           if (!Array.isArray(data)) {
               throw new Error('Invalid response format');
           }


           if (data.length === 0) {
               eventsList.innerHTML = '<p>No events found</p>';
               return;
           }


           data.forEach(event => {
               eventsList.appendChild(createEventElement(event));
           });
       } catch (error) {
           console.error('Error loading events:', error);
           showError('Error loading events. Please try again.');
           eventsList.innerHTML = '<p>Error loading events. Please try again.</p>';
       }
   }


   eventForm.addEventListener('submit', async (e) => {
       e.preventDefault();
       console.log('Form submitted');


       const startTime = document.getElementById('event-start').value;
       const endTime = document.getElementById('event-end').value;


       if (new Date(startTime) >= new Date(endTime)) {
           showError('End time must be after start time');
           return;
       }


       const eventData = {
           user_id: 1, // You might want to get this from your authentication system
           title: document.getElementById('event-title').value.trim(),
           description: document.getElementById('event-description').value.trim(),
           start_time: startTime,
           end_time: endTime
       };


       console.log('Sending event data:', eventData);


       try {
           const response = await fetch('/calendar/add', {
               method: 'POST',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify(eventData)
           });


           console.log('Add event response:', response);


           if (!response.ok) {
               const errorData = await response.json();
               throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
           }


           const result = await response.json();
           console.log('Add event result:', result);


           if (result.success === false) {
               throw new Error(result.message);
           }


           // Add the new event to the list
           if (result.event) {
               const eventElement = createEventElement(result.event);
               eventsList.insertBefore(eventElement, eventsList.firstChild);


               // Clear the form
               eventForm.reset();
               alert('Event added successfully!');


               // Reload events to ensure consistency
               loadEvents();
           }
       } catch (error) {
           console.error('Error adding event:', error);
           showError(`Error adding event: ${error.message}`);
       }
   });


   // Load events when the page loads
   loadEvents();
});
