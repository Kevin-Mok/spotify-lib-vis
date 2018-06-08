console.log("{{ user_id }}");
artist_data = JSON.parse('{{ artist_data }}');
artist_data.forEach(function(d) {
	console.log(d.name, d.num_songs);
});

d3.json("{% url "get_artist_data" user_id %}", function(error, data) {
	data.forEach(function(d) {
		console.log(d.name, d.num_songs);
	});
});
