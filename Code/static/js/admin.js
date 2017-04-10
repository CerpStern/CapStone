$(document).ready(function() {
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
	$('.approve').click(function(e) {
		let params = new URLSearchParams($(this).attr('href').slice(7)); // This is bad and depends on the length of the query string but works
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
		//console.log($(this).attr('href'));
		e.preventDefault();
	});
	$('.deny').click(function(e) {
		let params = new URLSearchParams($(this).attr('href').slice(7)); // This is bad and depends on the length of the query string but works
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
		//console.log($(this).attr('href'));
		e.preventDefault();
	});
});
