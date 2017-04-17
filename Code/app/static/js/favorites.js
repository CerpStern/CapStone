// enables Add to favorites button in materialize
var request = null;
$('#favorite').click(function() {
	$.ajax({
		url:'/favorite',
		type: 'POST',
		data: $('#fav_btn').serialize()
	});
});
