d3.json("{% url "get_artist_data", user_id %}").then(function(error, data) {
	data.forEach(function(d) {
		console.log(d.name, d.num_songs);
	});
});
