$(document).ready(function() {
	$('#add').submit(function(e) {
		$.ajax({
			url: '/add',
			type: 'POST',
			data: $('#add').serialize(),
			success: function(data) {
				console.log('Added!');
				if (data.status == "1")
					$('#addstate').html('<i class="material-icons">check_circle</i> Successfully Added!');
				else
					$('#addstate').html('<i class="material-icons">error</i> Adding Syllabus Failed!');
			}
		});
		e.preventDefault()
	});
});
