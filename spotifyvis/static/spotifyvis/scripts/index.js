document.getElementById("login-btn").addEventListener("click", function() {
    let httpRequest = new XMLHttpRequest();

    /*
     * Handler for the response
     */
    httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                // hide the login button
                document.getElementById('login').setAttribute("display", "none");

                let responseData = JSON.parse(httpRequest.responseText);
                let dataList = document.getElementById("data-list");
                

                for (let key in responseData) {
                    let newLi = document.createElement("li");
                    let innerList = document.createElement("ul");
                    
                    let dataLabel = document.createElement("li");
                    dataLabel.innerText = key;

                    let dataValue = document.createElement("li");
                    dataValue.innerText = responseData[key];

                    innerList.appendChild(dataLabel);
                    innerList.appendChild(dataValue);

                    newLi.appendChild(innerList);
                    dataList.appendChild(newLi);
                }
            } else {
                alert("There was a problem with the login request, please try again!");
            }
        }
    }

    httpRequest.open('GET', '/login', true);
    httpRequest.send();
});

