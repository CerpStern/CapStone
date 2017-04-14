function init_tinymce() {
	tinymce.init({
		selector: 'textarea',
		content_css: ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.98.0/css/materialize.min.css'],
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

$('#edit').click(function() {
	//$('#edit').onclick = function() {
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

$('#save').click(function() {
	//$('#edit').onclick = function() {
	console.log('clicked save');

	$('#save').css('display', 'none');
	$('#edit').css('display', 'inline');
});
