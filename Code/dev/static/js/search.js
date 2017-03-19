var request = null;
$(function() {
	$("#search").keyup(function() {
		console.log("received keyup");
		var foo = this;
		var value = $(this).val();
		var space = value.indexOf(' ');
		console.log(value);
		console.log(space);

		if (space != -1 && space != value.length - 1) {
			if (request != null)
				request.abort();
			request = $.ajax({
				type: "POST",
				url: "/search",
				data: {
					'searchword' : value
				},
				dataType: "text",
				success: function(msg) {
					if (value == $(foo).val()) {
						console.log(msg);
					}
				}
			});
		}
	});
});
