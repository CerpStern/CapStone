
var request = null;
$('#favorite').click(function() {
		$.ajax({
					url:'/favorite',
					type: 'POST',
					data: $('#fav_btn').serialize()
				});
});
