
// Initializes Parts of Materialize
$(document).ready(function() {
	$('select').material_select();
	$('#print').click(function(e) {
		e.preventDefault();
		window.print();
	});
});

// Enables click to search button
//   ( versus hitting enter )
var request = null;
$('#let_er_rip').click(function() {
	$.ajax({
		url:'/search',
		type: 'POST',
		data: $('#search_me').serialize()
	});
});


