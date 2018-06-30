/** Queries the backend for audio feature data, draws the bar chart
 *  illustrating the frequencies of values, and appends the chart to
 *  a designated parent element
 *
 *  @param audioFeature: the name of the audio feature (string)
 *  @param intervalEndPoints: a object defining the intervals (categories) of values,
 *  for example:
 *      {begin: 0, end: 1.0, step: 0.25} for instrumentalness would define ranges
 *      [0-0.25), [0.25-0.5), [0.5-0.75), [0.75-1.0]
 *  @param parentElem: the DOM element to append the graph to (a selector string)
 *  @param userSecret: the user secret string for identification
 *  @return None
 */
function drawAudioFeatGraph(audioFeature, intervalEndPoints, parentElem, userSecret) {
    // TODO: Not hard code the dimensions?
    let margin = {top: 20, right: 30, bottom: 30, left: 40};
    let width = 480 - margin.left - margin.right,
        height = 270 - margin.top - margin.bottom;

    let featureData = {};
    let currentEndPoint = intervalEndPoints.begin; // start at beginning
    // Create the keys first in order
    while (currentEndPoint < intervalEndPoints.end) {
        let startOfRange = currentEndPoint;
        let endOfRange = precise(startOfRange + intervalEndPoints.step);

        let key = `${startOfRange} ~ ${endOfRange}`;
        featureData[key] = 0;
        currentEndPoint = endOfRange;
    }
    // for (let index = 0; index < intervalEndPoints.length - 1; index++) {
    //     let key = `${intervalEndPoints[index]} ~ ${intervalEndPoints[index + 1]}`;
    //     featureData[key] = 0;
    // }
    // define the vertical scaling function
    let vScale = d3.scaleLinear().range([height, 0]);

    d3.json(`/api/audio_features/${audioFeature}/${userSecret}`)
        .then(function(response) {
        // categorize the data points
        for (let dataPoint of response.data_points) {
            dataPoint = parseFloat(dataPoint);
            let currLowerBound = precise(intervalEndPoints.end - intervalEndPoints.step);
            let stepSize = intervalEndPoints.step;
            // find the index of the first element greater than dataPoint
            while (dataPoint < currLowerBound && currLowerBound >= intervalEndPoints.begin) {
                currLowerBound = precise(currLowerBound - stepSize);
            }
            let upperBound = precise(currLowerBound + stepSize);
            currLowerBound = precise(currLowerBound);
            let key = `${currLowerBound} ~ ${upperBound}`;
            featureData[key] += 1;
        }

        let dataSet = Object.values(featureData);
        let dataRanges = Object.keys(featureData); // Ranges of audio features, e.g. 0-0.25, 0.25-0.5, etc
        let dataArr = [];
        // turn the counts into an array of objects, e.g. {range: "0-0.25", counts: 5}
        for (let i = 0; i < dataRanges.length; i++) {
            dataArr.push({
                range: dataRanges[i],
                counts: featureData[dataRanges[i]]
            });
        }
        vScale.domain([0, d3.max(dataSet)]).nice();

        let hScale = d3.scaleBand().domain(dataRanges).rangeRound([0, width]).padding(0.5);

        let xAxis = d3.axisBottom().scale(hScale);
        let yAxis = d3.axisLeft().scale(vScale);

        let featureSVG = d3.select(parentElem)
            .append('svg').attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);

        let featureGraph = featureSVG.append("g")
            .attr("transform", `translate(${margin.left}, ${margin.top})`)
            .attr("fill", "teal");

        featureGraph.selectAll(".bar")
            .data(dataArr)
            .enter().append('rect')
            .attr('class', 'bar')
            .attr('x', function(d) { return hScale(d.range); })
            .attr('y', function(d) { return vScale(d.counts); })
            .attr("height", function(d) { return height - vScale(d.counts); })
            .attr("width", hScale.bandwidth());

        // function(d) { return hScale(d.range); }

        featureGraph.append('g')
            .attr('class', 'axis')
            .attr('transform', `translate(0, ${height})`)
            .call(xAxis);

        featureGraph.append('g')
            .attr('class', 'axis')
            .call(yAxis);

        featureSVG.append("text")
            .attr('x', (width / 2))
            .attr('y', (margin.top / 2))
            .attr('text-anchor', 'middle')
            .style('font-size', '14px')
            .text(`${capFeatureStr(audioFeature)}`);

    });
}

/**
 * Returns the audio feature name string with the first letter capitalized
 * @param audioFeature: the name of the audio feature
 * @returns the audio feature name string with the first letter capitalized
 */
function capFeatureStr(audioFeature) {
    return audioFeature.charAt(0).toUpperCase() + audioFeature.slice(1);
}

/**
 * Converts a number to a floating point value with 2 significant figures
 * @param number: the number to be converted
 * @returns the input converted to two significant digits
 */
function precise(number) {
    return Number.parseFloat(number.toPrecision(2));
}