/**
 * Retrieves data for a specific audio feature for a certain user
 * @param audioFeature: the audio feature for which data will be retrieved
 * @param clientSecret: the client secret, needed for security
 */
function getAudioFeatureData(audioFeature, userSecret) {
    let httpRequest = new XMLHttpRequest();
    /*
     * Handler for the response
     */
    httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                let responseData = JSON.parse(httpRequest.responseText);
                // TODO: The data points need to be plotted instead
                for (let data of responseData.data_points) {
                    console.log(data);
                }
            } else {
                alert("There was a problem with the login request, please try again!");
            }
        }
    };

    let queryString = `/audio_features/${audioFeature}/${userSecret}`;
    httpRequest.open('GET', queryString, true);
    httpRequest.send();
}