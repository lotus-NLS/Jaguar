function appendMessage(msg) {
    let chatWindow = document.getElementById('chat-window');
    let newElement = document.createElement('div');
    newElement.innerHTML = '<p>User: ' + msg + '</p>';
    chatWindow.appendChild(newElement);
}


//TODO: Before the event listening starts, should verify that the object even exists
//else wait or raise Exception
document.addEventListener('DOMContentLoaded', function(){
    console.log('Document loaded!');

    let dash_container = document.getElementById('_dash-app-content');
    if (dash_container) {
        dash_container.addEventListener('click', function(event) {
            if (event.target.id === 'Send') {
                 console.log('Send button clicked!');

                let inputElem = dash_container.querySelector('#text_bar');
                if (inputElem) {
                    console.log('Text input element found')
                    let inputValue = inputElem.value;
                    console.log('Text element has value ' + inputValue)
                    appendMessage(inputValue);  // Append the message
                    // inputElem.value = '';  // Reset the input field
                }
                else{
                    console.log('Input field not found!');
                }
            }
        });
    } else {
        console.log('_dash-app-content not found!');
    }
});
