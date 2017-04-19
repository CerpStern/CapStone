$(document).ready(function() {
	// Asynchronously add a new Course
	$('#add').submit(function(e) {
		$.ajax({
			url: '/add',
			type: 'POST',
			data: $('#add').serialize(),
			success: function(data) {
				console.log('Added!');
				if (data.status == "1")
					$('#addstate').html('<i class="material-icons green-text">check_circle</i> Successfully Added!');
				else
					$('#addstate').html('<i class="material-icons red-text">error</i> Adding Syllabus Failed!');
			}
		});
		e.preventDefault();
	});
	// Asynchronously remove a Course
	$('#remove').submit(function(e) {
		$.ajax({
			url: '/remove',
			type: 'POST',
			data: $('#remove').serialize(),
			success: function(data) {
				console.log('Removing!');
				if (data.status == "1")
					$('#remstate').html('<i class="material-icons green-text">check_circle</i> Successfully Removed!');
				else
					$('#remstate').html('<i class="material-icons red-text">error</i> Removing Syllabus Failed!');
			}
		});
		e.preventDefault();
	});
	// Asynchronously add an administrator
	$('#addadmin').submit(function(e) {
		$.ajax({
			url: '/addadmin',
			type: 'POST',
			data: $('#addadmin').serialize(),
			success: function(data) {
				console.log('Adding!');
				if (data.status == "1")
					$('#addadminstate').html('<i class="material-icons green-text">check_circle</i> Successfully Added!');
				else
					$('#addadminstate').html('<i class="material-icons red-text">error</i> Adding Admin Failed!');
			}
		});
		e.preventDefault();
	});
	// Asynchronously remove an administrator
	$('#remadmin').submit(function(e) {
		$.ajax({
			url: '/remadmin',
			type: 'POST',
			data: $('#remadmin').serialize(),
			success: function(data) {
				console.log('Adding!');
				if (data.status == "1")
					$('#remadminstate').html('<i class="material-icons green-text">check_circle</i> Successfully Removed!');
				else
					$('#remadminstate').html('<i class="material-icons red-text">error</i> Removing Admin Failed!');
			}
		});
		e.preventDefault();
	});
	// Asynchronously approve/deny a syllabus
	var queue = function(e) {
		let params = new URLSearchParams($(this).attr('href').slice(7));
		console.log(params.get('id'));
		console.log(params.get('action'));
		$.ajax({
			url: $(this).attr('href'),
			type: 'GET',
			success: function(data) {
				$("."+params.get('id')).remove();
				console.log('Success!');
			}
		});
		e.preventDefault();
	};
	// Connect handlers for approving and denying to queue function
	$('.approve').click(queue);
	$('.deny').click(queue);
});
