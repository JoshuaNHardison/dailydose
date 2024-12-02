document.addEventListener('DOMContentLoaded', function () {
    // Attach click event to each card-color div
    document.querySelectorAll('.card-color').forEach(function (card) {
        card.onclick = function () {
            let link = card.getAttribute('data-link');
            let triviaID = card.getAttribute('data-trivia-id');
            let hasPlayedToday = card.getAttribute('data-played') === 'true';

            console.log('link: ', link)

            if (!link){
                console.log('getting parent element')
                link = card.parentElement.getAttribute('data-link');
                triviaID = card.parentElement.getAttribute('data-trivia-id');
                hasPlayedToday = card.parentElement.getAttribute('data-played') === 'true';
            }
            // Open the link in a new tab
            window.open(link, '_blank');
            // Automatically mark the "played" checkbox as checked
            if (!hasPlayedToday) {
                let playedCheckbox = document.getElementById(`playedCheckbox-${triviaID}`);
                console.log('checkbox: ', playedCheckbox);
                console.log('triviaID: ', triviaID)
                if (!playedCheckbox) {
                playedCheckbox = document.querySelector(`#playedCheckbox-${triviaID}`);
                console.log('checkbox: ', playedCheckbox);
                }
                playedCheckbox.checked = true;

                // Show the 'won' checkbox when 'played' is checked
                toggleWonCheckboxVisibility(triviaID, true);

                // Send "played" status to the server
                handleCheckboxChange(triviaID, 'played', true);
            }

        };
    });

    // Function to handle checkbox changes
    function handleCheckboxChange(triviaID, type, status = null) {
        const checkbox = document.getElementById(`${type}Checkbox-${triviaID}`);
        const checkboxStatus = checkbox.checked;

        if (type === 'played'){
            const wonCheckbox = document.getElementById(`wonCheckbox-${triviaID}`);
            if (wonCheckbox) {
                wonCheckbox.checked = false;

                handleCheckboxChange(triviaID, 'won', false);
            }
        }


        if (checkboxStatus) {
            // Send data to the server
            fetch(`/create_or_update_trivia_record/${triviaID}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `type=${type}&status=true` // Send either "played" or "won" with its current state
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        hasPlayedToday = true;
                        console.log(`${type.charAt(0).toUpperCase() + type.slice(1)} status updated successfully for Trivia ID ${triviaID}.`);
                    } else {
                        console.error(`Failed to update ${type} status: ${data.message}`);
                    }
                })
                .catch(error => console.error('Error:', error));
        }else {
            fetch(`/delete_trivia_attempt/${triviaID}/`, {
                method: 'POST',
                headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `type=${type}&status=false`
            })
            .then(response=>response.json())
            .then(data=> {
                if (data.success){
                    console.log(`Type of ${type} deleted for TriviaID: ${triviaID}`);
                } else {
                    console.log(`Failed to delete attempt: ${data.message}`);
                    console.log(`$type is ${type} and checkboxstatus is ${checkboxStatus}`);
                }
            })
            .catch(error => console.error('Error: ', error));
        }
    }

    function toggleWonCheckboxVisibility(triviaID, show) {
        const wonCheckboxContainer = document.getElementById(`wonCheckbox-${triviaID}`).closest('.checkbox-container');
        if (wonCheckboxContainer) {
            wonCheckboxContainer.style.display = show ? 'flex' : 'none';
        }
    }

    // Attach onchange event to all played and won checkboxes
    document.querySelectorAll('input[type="checkbox"][name="playedCheckbox"]').forEach(function (checkbox) {
        checkbox.onchange = function () {
            const triviaID = this.id.split('-')[1];
            handleCheckboxChange(triviaID, 'played');
            toggleWonCheckboxVisibility(triviaID, this.checked)
        };
    });

    document.querySelectorAll('input[type="checkbox"][name="wonCheckbox"]').forEach(function (checkbox) {
        checkbox.onchange = function () {
            const triviaID = this.id.split('-')[1];
            handleCheckboxChange(triviaID, 'won');
        };
    });

    document.querySelectorAll('input[type="checkbox"][name="playedCheckbox"]').forEach(function (checkbox) {
        if (checkbox){
        const triviaID = checkbox.id.split('-')[1];
        const wonCheckboxContainer = checkbox.closest('.checkbox-container')?.nextElementSibling;
        if (wonCheckboxContainer) {
        toggleWonCheckboxVisibility(triviaID, checkbox.checked)
        }
    }
    })
});
