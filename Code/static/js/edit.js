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
$('#edit').onclick = function() {
	var i = 0;
	$('#syllabus').children().each(function () {
		++i;
		this.innerHTML = '<textarea name="test' + i + '">' + this.innerHTML + '</textarea>';
	});
	init_tinymce();
}
