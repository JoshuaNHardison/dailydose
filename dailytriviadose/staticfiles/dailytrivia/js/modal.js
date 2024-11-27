// Modal Functionality
document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById('myModal');
    var confirmModal = document.getElementById('confirmationModal');
    var iframe = document.getElementById('modalIframe');
    var span = document.getElementsByClassName('close')[0];
    var confirmCloseButton = document.getElementById('confirmClose');
    var playedCheckbox = document.getElementById('playedCheckbox');
    var wonCheckbox = document.getElementById('wonCheckbox');
    var currentTriviaID = null;
    var alreadyPlayedToday = false;


//     // Function to handle checkbox changes
//     function handleCheckboxChange(triviaID, type) {
//     // Identify the checkbox
//     const checkbox = document.getElementById(`${type}Checkbox-${triviaID}`);
//     const status = checkbox.checked; // Get the current state of the checkbox

//     // Send data to the server
//     fetch(`/create_or_update_trivia_record/${triviaID}/`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/x-www-form-urlencoded',
//             'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
//         },
//         body: `${type}=${status}` // Send either "played" or "won" with its current state
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             console.log(`${type.charAt(0).toUpperCase() + type.slice(1)} status updated successfully for Trivia ID ${triviaID}.`);
//         } else {
//             console.error(`Failed to update ${type} status: ${data.message}`);
//         }
//     })
//     .catch(error => console.error('Error:', error));
// }

    
    // Function to open modal with specific link
    function openModalWithLink(link, triviaID, hasPlayedToday) {
        iframe.src = link;
        modal.style.display = 'block';
        // currentTriviaID = triviaID;
        // alreadyPlayedToday = hasPlayedToday;
        // console.log("open modal: ", triviaID, "already played: ", alreadyPlayedToday)
    }

    // Attach click event to each button with the class
    document.querySelectorAll('.card-color').forEach(function(card) {
        card.onclick = function() {
            var link = card.getAttribute('data-link');
            var triviaID = card.getAttribute('data-trivia-id')
            var hasPlayedToday = card.getAttribute('data-played') === 'true';
            var embed = card.getAttribute('data-embed') === 'true';

            currentTriviaID = triviaID;
            alreadyPlayedToday = hasPlayedToday;

            if (hasPlayedToday) {
                return;
            }

            if (embed) {
                openModalWithLink(link, triviaID, hasPlayedToday);
            }
            else {
                window.open(link, '_blank');
                if (!hasPlayedToday) {
                    currentTriviaID = triviaID;
                    confirmModal.style.display = 'block';
                }
            }

            // console.log("trivia ID: ", triviaID, "data-played: ", hasPlayedToday);

            // openModalWithLink(link, triviaID, hasPlayedToday);
        };
    });

    confirmCloseButton.onclick = function() {
        closeConfirmModal()
    }

    // Close the modal when the user clicks on <span> (x)
    span.onclick = function() {
        closeModal();
    }


    // Close the modal when the user clicks anywhere outside of the modal
    window.onclick = function(event) {
        if (event.target == modal) {
            closeModal();
        } else if (event.target == confirmModal) {
            closeConfirmModal();
        }
    }

    function closeModal() {
        modal.style.display = 'none';
        iframe.src = '';
        if (!alreadyPlayedToday){
            confirmModal.style.display = 'block';
        }
    }

    // document.querySelectorAll('.openSiteButton').forEach(function(button){
    //     button.onclick = function() {
    //         var link = button.getAttribute('data-link');
    //         var triviaID = button.getAttribute('data-trivia-id');
    //         var isEligible = button.getAttribute('data-eligible') === 'true';
    //         console.log("trivia id: ", triviaID, "isEligible: ", isEligible)
    //         window.open(link, '_blank');
            

    //         if(isEligible) {
    //             currentTriviaID = triviaID;
    //             confirmModal.style.display = 'block';
    //         }
    //     }
    // })

    function updatePlayedStatus(triviaID) {
        var playedStatusSpan = document.getElementById('playedStatus-' + triviaID);
        if (playedStatusSpan) {
            playedStatusSpan.textContent = 'Already Played Today';
            playedStatusSpan.style.display = 'inline';
        }
    }

    function closeConfirmModal() {
        updatePlayedStatus(currentTriviaID);
        confirmModal.style.display = 'none'
        
        var played = playedCheckbox.checked;
        var won = wonCheckbox.checked;
        
        fetch(`/create_or_update_trivia_record/${currentTriviaID}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `played=${played}&won=${won}`
        })
        .then(response => {
            console.log('Response Status: ', response.status);
            return response.json();
        })
        .then(data => {
            if (data.success){
                alreadyPlayedToday = true;
                updatePlayedStatus(currentTriviaID)
                if (data.created){
                    console.log('New TGR created and updated.')
                } else{
                console.log('Existing TGR updated.')

                }
            } else {
                console.error('Failed', data.message)
            }
        })
        .catch(error => console.error('Error: ', error));

        console.log('Atempted: ', played, 'Won: ', won)

        playedCheckbox.checked = true;
        wonCheckbox.checked = false;
    }
});