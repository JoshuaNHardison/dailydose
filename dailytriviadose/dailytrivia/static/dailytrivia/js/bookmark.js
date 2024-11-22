document.addEventListener('DOMContentLoaded', function() {
    const bookmarkButtons = document.querySelectorAll('.bookmark');

    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
            const triviaID = this.getAttribute('data-trivia-id');
            fetch(`/toggle_bookmark/${triviaID}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            })
        .then(response => {
            if (!response.ok){
                throw new Error(`http error: ${response.status}`)
            }
            return response.json();
        })
        .then(data => {
            const svgPath = this.querySelector('svg path');


            if (data.is_bookmarked){
                svgPath.style.fill = 'red';
            } else {
                svgPath.style.fill = '';
            }
        })
        .catch(error => console.error("error: ", error));
        })
    })
})
