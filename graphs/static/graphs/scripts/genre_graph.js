function create_genre_graph(data) {
    // convert strings to nums {{{ //
    
    data.forEach(function(d) {
        d.num_songs = +d.num_songs;
        console.log(d.genre, d.num_songs);
        let artist_names = Object.keys(d.artists);
        artist_names.forEach(function(e) {
            d.artists[e] = +d.artists[e];
            console.log(e, d.artists[e]);
            //console.log(e, d.artists[e], d.artists[e] + 1);
        });
    });
    
    // }}} convert strings to nums //

	// domains {{{ //
	
    data.sort(function(a, b) {
        return b.num_songs - a.num_songs;
    });
    x.domain(data.map(function(d) {
        return d.genre;
    }));
    //y.domain([0, d3.max(data, function(d) { return d.num_songs; }) * 1.25]).nice();
    y.domain([0, d3.max(data, function(d) {
        return d.num_songs;
    })]).nice();
	
	// }}} domains  //

    // setup bar colors {{{ //
    
    let max_artists = d3.max(data, function(d) {
        return Object.keys(d.artists).length;
    });
    let z = d3.scaleOrdinal().range(randomColor({
        count: max_artists,
        luminosity: 'light',
    }));
    
    // }}} setup bar colors //

    for (let genre_dict of data) {
		
        // process artist breakdown  {{{ //
        
        let keys = Object.keys(genre_dict.artists);
        let stack = d3.stack()
            //.order(d3.stackOrderAscending)
            .order(d3.stackOrderDescending)
            .keys(keys)([genre_dict.artists])
            //unpack the column
            .map((d, i) => {
                return {
                    key: keys[i],
                    data: d[0]
                }
            });
        
        // }}} process artist breakdown  //

        // add bars {{{ //
        
        g.append("g")
            .selectAll("rect")
            .data(stack)
            .enter().append("rect")
            .attr("x", x(genre_dict.genre))
            .attr("y", function(d) {
                return y(d.data[1]);
            })
            .attr("height", d => y(d.data[0]) - y(d.data[1]))
            .attr("width", x.bandwidth())
            .attr('fill', (d, i) => z(i))
            .append('title').text(d => d.key + ': ' + (d.data[1] - d.data[0]));
        
        // }}} add bars //

        // x-axis {{{ //
        
        g.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x))
            .selectAll(".tick text")
            .call(wrap, x.bandwidth());
        
        // }}} x-axis //

        // y-axis {{{ //
        
        g.append("g")
            .attr("class", "axis")
            .call(d3.axisLeft(y).ticks(null, "s"))
            .append("text")
            .attr("x", 2)
            .attr("y", y(y.ticks().pop()) + 0.5)
            .attr("dy", "0.32em")
            .attr("fill", "#000")
            .attr("font-weight", "bold")
            .attr("text-anchor", "start")
            .text("Songs");
        
        // }}} y-axis //

    }
}

// wrap text {{{ //

// https://gist.github.com/guypursey/f47d8cd11a8ff24854305505dbbd8c07#file-index-html
function wrap(text, width) {
    text.each(function() {
        let text = d3.select(this),
			words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1, // ems
            y = text.attr("y"),
            dy = parseFloat(text.attr("dy")),
            tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em")
        while (word = words.pop()) {
            line.push(word)
            tspan.text(line.join(" "))
            if (tspan.node().getComputedTextLength() > width) {
                line.pop()
                tspan.text(line.join(" "))
                line = [word]
                tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", `${++lineNumber * lineHeight + dy}em`).text(word)
            }
        }
    })
}

// }}} wrap text //
