/**
 * Draws the artist count graph as a bubble chart, and appends it the a designated parent element
 * @param artistData: the artist counts data as an array of objects, of the format {'name': artist name, 'num_songs': 50}
 * @param parentElem: the DOM element to append the artist graph to (as a string)
 */
function drawArtistGraph(artistData, parentElem) {
    let margin = {top: 20, right: 30, bottom: 30, left: 40};
    // let width = 1000 - margin.right - margin.left;
    // let height = 1000 - margin.top - margin.bottom;

    let color = d3.scaleOrdinal(d3.schemeCategory10);
    /*
    ** Next four variables were part of an attempt to make bubbles larger,
    ** didn't work
     */
    let songCounts = artistData.children.map(function(artist) { return artist.num_songs; }); // array of counts
    let songCountExtent = d3.extent(songCounts); // [min song count, max song count]
    let circleSize = {
        min: 45,
        max: 75
    };
    let circleRadiusScale = d3.scaleSqrt().domain(songCountExtent).range([circleSize.min, circleSize.max]);

    let bubble = d3.pack(artistData)
        // .size([width + 100, height + 100])
        .size([600, 250])
        .padding(0.2);

    let svg = d3.select(parentElem)
        // .append("svg")
        // .attr("width", width + margin.right + margin.left)
        // .attr("height", height + margin.top + margin.bottom)
        // .attr("class", "bubble");
        .append("div")
        .classed("svg-container", true) //container class to make it responsive
        .append("svg")
        //responsive SVG needs these 2 attributes and no width and height attr
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "0 0 600 250")
        //class to make it responsive
        .classed("svg-content-responsive", true); 

    let nodes = d3.hierarchy(artistData)
        .sum(function(d) { return d.num_songs; });

    let node = svg.selectAll(".node")
        .data(bubble(nodes).leaves())
        .enter()
        .filter(function(d) {
            return !d.children;
        })
        .append("g")
        .attr("class", "node")
        .attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

    node.append("title")
        .text(function(d) {
            return d.data.name + ": " + d.data.num_songs;
        });

    node.append("circle")
        .attr("r", function(d) {
            return d.r;
        })
        .style("fill", function(d,i) {
            return color(i);
        });

    // artist name text
     node.append("text")
        .attr("dy", ".2em")
        .style("text-anchor", "middle")
        .text(function(d) {
            return d.data.name.substring(0, d.r / 3);
        })
        .attr("font-family", "sans-serif")
        .attr("font-size", function(d){
            return d.r/5;
        })
        .attr("fill", "white");

     // artist song count text
     node.append("text")
        .attr("dy", "1.3em")
        .style("text-anchor", "middle")
        .text(function(d) {
            return d.data.num_songs;
        })
        .attr("font-family",  "Gill Sans", "Gill Sans MT")
        .attr("font-size", function(d){
            return d.r/5;
        })
        .attr("fill", "white");

     d3.select(self.frameElement)
         // .style("height", height + "px");
         .style("height", "100%")



}
