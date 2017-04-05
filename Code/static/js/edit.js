function init_tinymce() {
	tinymce.init({
		selector: 'textarea',
		height: 500,
		menubar: false,
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
	console.log('clicked');
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
