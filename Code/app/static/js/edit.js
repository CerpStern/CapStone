// Does what it says on the tin, initializes the editor
function init_tinymce() {
	tinymce.init({
		selector: 'textarea',
		//content_css: ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.98.0/css/materialize.min.css'],
		height: 500,
		menubar: false,
		mode : "textareas",
		force_br_newlines : false,
		force_p_newlines : false,
		forced_root_block : '',
		plugins: [
			'save code advlist autolink lists link image charmap',
			'hr',
			'textcolor'
		],
		toolbar: 'save code | undo redo | fontsizeselect forecolor bold italic underline | alignleft aligncenter alignright | bullist numlist outdent indent | subscript superscript | removeformat | hr charmap link image',
	});
}

// Insert the editors
$('#edit').click(function() {
	console.log('clicked edit');

	$('#edit').css('display', 'none');
	$('#save').css('display', 'inline');

	var i = 1;
	$('#syllabus').children().each(function () {
		console.log($(this));
		let id = $(this).attr('id');
		console.log($(this).html);
		if (id) {
			++i;
			$(this).html('<textarea name="test' + i + '">' + $(this).html() + '</textarea>');
		}
	});
	init_tinymce();
});

// Save the syllabus
$('#save').click(function() {

	$('#save').css('display', 'none');
	$('#edit').css('display', 'inline');
	$('#syllform').submit();
});

// Asynchronously remove professor from a course
$('#remprof').click(function(e) {
	e.preventDefault();
	console.log('clicky');
	let params = new URLSearchParams($(this).attr('href').slice(9));
	console.log(params.get('id'));
	// Create a form
	let form = jQuery('<form>', {
		'action': '/remprof'
	}).append(jQuery('<input>', {
		'name': 'id',
		'value': params.get('id')
	}));
	$.ajax({
		url: '/remprof',
		type: 'POST',
		data: form.serialize(),
		success: function(data) {
			if (data.status == "1") {
				location.reload();
			}
		}
	});
});
// Asynchronously set a professor for a course
$('#setinstform').submit(function(e) {
	e.preventDefault();
	$.ajax({
		url: '/setprof',
		type: 'POST',
		data: $('#setinstform').serialize(),
		success: function(data) {
			console.log('Adding!');
			if (data.status == "1") {
				location.reload();
			}
		}
	});
});
