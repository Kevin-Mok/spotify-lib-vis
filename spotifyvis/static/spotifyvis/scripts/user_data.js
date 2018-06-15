/**
 * Retrieves data for a specific audio feature for a certain user
 * @param audioFeature: the audio feature for which data will be retrieved
 * @param clientSecret: the client secret, needed for security
 * @param chartElement: the SVG element in which the data will be plotted
 */
function plotAudioFeatureData(audioFeature, userSecret, chartElement) {
    let httpRequest = new XMLHttpRequest();
    /*
     * Handler for the response
     */
    httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                let responseData = JSON.parse(httpRequest.responseText);

            } else {
                alert("There was a problem with the login request, please try again!");
            }
        }
    };

    let queryString = `/audio_features/${audioFeature}/${userSecret}`;
    httpRequest.open('GET', queryString, true);
    httpRequest.send();
}